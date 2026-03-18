import argparse
import json
import time
import re
import os
from pathlib import Path
from dataclasses import dataclass

from adapters.llm.llm_adapter import LLMAdapter
from core.event_bus import BUS, EventBus
from core.event_types import EventTypes
from self_improve.error_analyzer import ErrorAnalyzer
from workflows.runner import run_workflow, load_workflow


ROOT = Path(os.environ.get("GRAYWOLF_ROOT", Path(__file__).resolve().parents[1]))
TOOLS_DIR = ROOT / "tools"
SCRIPTS_DIR = ROOT / "scripts"
WORKFLOWS_DIR = ROOT / "workflows"
LOGS_DIR = ROOT / "logs"


def _tool_path(tool_name: str) -> str:
    return str(TOOLS_DIR / tool_name)


def _script_path(script_name: str) -> str:
    return str(SCRIPTS_DIR / script_name)


def _workflow_path(workflow_name: str) -> str:
    return str(WORKFLOWS_DIR / workflow_name)


@dataclass
class OrchestratorStep:
    name: str
    instruction: str
    max_retries: int = 0
    retry_delay_seconds: float = 1.0


class Orchestrator:
    """Faz 2: plan -> tool -> evaluate (+ retry/backoff + error classification)"""

    def __init__(self, llm: LLMAdapter, max_retries: int = 2, backoff_seconds: float = 1.0, event_bus: EventBus | None = None):
        self.llm = llm
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.error_analyzer = ErrorAnalyzer()
        self.bus = event_bus or BUS

    @staticmethod
    def safe_sleep(seconds: float):
        time.sleep(seconds)

    @staticmethod
    def classify_error(error: Exception) -> str:
        msg = str(error).lower()
        if "api key" in msg or "auth" in msg or "token" in msg:
            return "auth_error"
        if "429" in msg or "rate" in msg or "quota" in msg:
            return "rate_limit"
        if "timeout" in msg:
            return "timeout"
        if "network" in msg or "connection" in msg or "dns" in msg:
            return "network_error"
        return "unknown_error"

    def plan(self, goal: str) -> list[OrchestratorStep]:
        prompt = (
            "En fazla 3 satır üret. Her satır formatı: step_name|shell_command\n"
            "Sadece gerçek shell komutu yaz. Çıplak tool adı YAZMA (ör: analysis_tool YAZMA).\n"
            "GrayWolf tool kullanacaksan python3 ile tam yol ver: "
            f"python3 {TOOLS_DIR}/<tool>.py ...\\n"
            f"Risk özeti için tercih edilen komut: {_script_path('risk_summary_from_terminal.sh')}\\n"
            "Dosyaya yazmak için güvenli hedefler: logs/, reports/, tasks/.\n"
            "Örnek: write_report|echo 'metin' > logs/report.md\n"
            "Sadece komut yaz, açıklama yazma.\n"
            f"Goal: {goal}"
        )

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                raw = self.llm.generate_response(prompt)
                if isinstance(raw, (tuple, list)):
                    raw = raw[0]
                return self._parse_steps(raw)
            except Exception as e:
                last_error = e
                category = self.classify_error(e)
                if category in {"auth_error", "unknown_error"}:
                    break
                if attempt < self.max_retries:
                    self.safe_sleep(self.backoff_seconds * (2 ** attempt))

        if last_error:
            raise RuntimeError(
                f"plan_failed category={self.classify_error(last_error)} error={last_error}"
            )
        return []

    def _parse_steps(self, raw: str) -> list[OrchestratorStep]:
        steps: list[OrchestratorStep] = []
        for line in raw.splitlines():
            if "|" not in line:
                continue
            name, instruction = line.split("|", 1)
            name = name.strip()
            instruction = self._normalize_instruction(instruction.strip())
            instruction = self._apply_quality_filter(instruction)
            if name and instruction:
                steps.append(OrchestratorStep(name=name, instruction=instruction))

        if not steps:
            steps.append(
                OrchestratorStep(
                    name="fallback_status_report",
                    instruction=f"python3 {_tool_path('status_reporter.py')} --summary --points 8 > logs/autonomy_live_report.md",
                )
            )
        return steps[:3]

    @staticmethod
    def _apply_quality_filter(instruction: str) -> str:
        cmd = (instruction or "").strip()
        if not cmd:
            return cmd

        disallowed_tokens = ["rm -rf /", "mkfs", "shutdown", "reboot", "poweroff", "dd if="]
        if any(tok in cmd for tok in disallowed_tokens):
            return "echo 'blocked_by_quality_filter'"

        # Prevent bare tool names from being treated as binaries.
        bare_tools = ["analysis_tool", "code_tool", "status_reporter", "report_tool"]
        if cmd in bare_tools:
            return f"python3 {_tool_path('status_reporter.py')} --summary --points 8 > logs/autonomy_live_report.md"

        return cmd

    @staticmethod
    def _normalize_instruction(instruction: str) -> str:
        cmd = instruction or ""
        m = re.search(r"(/[^\s]*/tools/)([a-zA-Z0-9_\-]+\.py)", cmd)
        if not m:
            return cmd

        full_prefix = m.group(1)
        tool_file = m.group(2)
        tool_path = TOOLS_DIR / tool_file
        if tool_path.exists():
            return cmd.replace(f"{full_prefix}{tool_file}", str(tool_path))

        alias_map = {
            "graywolf_status_reporter.py": "status_reporter.py",
            "gw_autonomy_monitor.py": "status_reporter.py",
            "autonomy_state_summary_tool.py": "status_reporter.py",
            "status_reporter.py": "status_reporter.py",
            "autonomy_summary_tool.py": "autonomy_summary_tool.py",
        }
        replacement = alias_map.get(tool_file, "status_reporter.py" if tool_file.endswith("_reporter.py") else "status_reporter.py")
        return cmd.replace(f"{full_prefix}{tool_file}", str(TOOLS_DIR / replacement))

    def execute_plan(self, steps: list[OrchestratorStep]) -> dict:
        workflow = {
            "name": "orchestrator-plan",
            "steps": [{"name": s.name, "cmd": s.instruction} for s in steps],
        }
        result = run_workflow(workflow)
        replan_payload = self._run_replan_if_needed(workflow.get("name"), result)
        if replan_payload:
            result.setdefault("replan", {})
            result["replan"].update(replan_payload)
        return result

    def _run_replan_if_needed(self, workflow_name: str | None, workflow_result: dict) -> dict | None:
        replan_info = self.replan_on_failure(workflow_result)
        if replan_info.get("status") != "replan_ready":
            return None

        self._publish_replan_ready(workflow_name, replan_info)

        replan_steps = replan_info.get("new_plan", [])
        if not replan_steps:
            execution = {"status": "skipped", "results": []}
            self._publish_replan_executed(workflow_name, replan_info, execution)
            return {"info": replan_info, "steps": [], "execution": execution}

        replan_workflow = {
            "name": f"replan-{workflow_name or 'plan'}",
            "steps": [
                {
                    "name": step.get("name"),
                    "cmd": step.get("cmd") or step.get("instruction"),
                }
                for step in replan_steps
            ],
        }
        replan_execution = run_workflow(replan_workflow)
        self._publish_replan_executed(workflow_name, replan_info, replan_execution)
        return {
            "info": replan_info,
            "steps": replan_steps,
            "execution": replan_execution,
        }

    def _publish_replan_ready(self, workflow_name: str | None, replan_info: dict) -> None:
        payload = {
            "workflow_name": workflow_name,
            "hint": replan_info.get("hint"),
            "original_error": replan_info.get("original_error"),
            "new_plan": replan_info.get("new_plan"),
            "info": replan_info,
        }
        self.bus.publish(EventTypes.REPLAN_READY, payload)

    def _publish_replan_executed(self, workflow_name: str | None, replan_info: dict, execution: dict) -> None:
        payload = {
            "workflow_name": workflow_name,
            "hint": replan_info.get("hint"),
            "replan_info": replan_info,
            "replan_result": execution,
        }
        self.bus.publish(EventTypes.REPLAN_EXECUTED, payload)

    def evaluate(self, execution_result: dict) -> str:
        statuses = [f"{r['name']}:{r['status']}" for r in execution_result.get("results", [])]
        return " | ".join(statuses) if statuses else "no-steps"

    def classify_workflow_error(self, workflow_result: dict) -> dict:
        error_summary = {"status": "ok", "categories": [], "details": []}
        for step_result in workflow_result.get("results", []):
            if step_result.get("status") in {"error", "timeout", "blocked", "needs_confirmation"}:
                stderr = step_result.get("stderr", "")
                analysis = self.error_analyzer.classify_failure(stderr)
                error_category = analysis["category"]

                if step_result.get("status") == "timeout":
                    # Timeout status deserves specific hint
                    error_category = "timeout"

                error_summary["categories"].append(error_category)
                error_summary["details"].append({
                    "step_name": step_result.get("name"),
                    "status": step_result.get("status"),
                    "error_category": error_category,
                    "stderr_snippet": stderr[:100],
                    "hint": analysis.get("replan_hint"),
                })
        if error_summary["categories"]:
            error_summary["status"] = "errors_found"
        return error_summary

    def mock_replan(self, hint: str) -> list[OrchestratorStep]:
        return [
            OrchestratorStep(name="replan_inspect", instruction=f"echo 'Inspecting hint: {hint}'"),
            OrchestratorStep(name="replan_retry", instruction="echo 'Retrying workflow with adjusted inputs'"),
        ]

    def replan_on_failure(self, workflow_result: dict) -> dict:
        classification = self.classify_workflow_error(workflow_result)
        if classification["status"] == "ok" or not classification["details"]:
            return {"status": "no_replan_needed"}

        first_detail = classification["details"][0]
        hint = self.error_analyzer.replan_hint_for_category(first_detail.get("error_category", "unknown_error"))
        new_plan = [step.__dict__ for step in self.mock_replan(hint)]
        return {
            "status": "replan_ready",
            "hint": hint,
            "new_plan": new_plan,
            "original_error": first_detail,
        }

    def run_self_improve(self, log_path: str | None = None) -> dict:
        if log_path is None:
            log_path = str(LOGS_DIR / "terminal.log")
        # 1. Log analizi workflow'unu çalıştır
        workflow_path = _workflow_path("self_improve_log_analysis.yaml")
        workflow_definition = load_workflow(workflow_path) # Workflow tanımını yükle
        workflow_result = run_workflow(workflow_definition) # Yüklenen tanımı run_workflow'a ilet

        if workflow_result.get("status") != "success":
            return {"status": "error", "error": "Self-improve workflow failed", "details": workflow_result}

        # 2. Analiz raporunu workflow sonucundan al
        latest_report = ""
        for step_result in workflow_result.get("results", []):
            if step_result.get("name") == "analyze_logs_with_llm":
                latest_report = step_result.get("stdout", "")
                break
        
        if not latest_report: # Eğer rapor boşsa veya okunamadıysa
             return {"status": "warning", "message": "Analiz raporu boş veya okunamadı.", "details": workflow_result}

        # 3. LLM'den bu önerilerden yeni görevler planlamasını iste
        prompt_for_tasks = (
            f"Aşağıdaki performans iyileştirme önerilerini incele ve GrayWolf için uygulanabilir, "
            f"en fazla 3 adet yeni görev planı oluştur. Her görev 'step_name|shell_command' formatında olmalı. "
            f"Sadece komutları döndür, açıklama veya ek metin ekleme.\n\nÖneriler: {latest_report}"
        )
        try:
            new_tasks_raw = self.llm.generate_response(prompt_for_tasks)
            new_tasks_text = new_tasks_raw[0] if isinstance(new_tasks_raw, (tuple, list)) else new_tasks_raw
            new_steps = self._parse_steps(new_tasks_text or "")
            return {"status": "ok", "message": "Yeni iyileştirme görevleri oluşturuldu.", "new_steps": [s.__dict__ for s in new_steps]}
        except Exception as e:
            return {"status": "error", "error": f"İyileştirme önerilerinden görev planlama hatası: {e}"}


def main() -> None:
    parser = argparse.ArgumentParser(description="GrayWolf Orchestrator")
    parser.add_argument("--goal", default="demo")
    parser.add_argument("--provider", choices=["router", "stub"], default="stub")
    parser.add_argument("--action", choices=["plan_execute", "run_self_improve"], default="plan_execute", help="Yapılacak eylem")
    args = parser.parse_args()

    if args.provider == "stub":

        class _StubLLM(LLMAdapter):
            def generate_response(self, prompt: str, **kwargs) -> tuple[str, int, int]:
                if "iyileştirme önerilerini incele" in prompt:
                    return "t1|echo \"İyileştirme Görevi A\"\nt2|echo \"İyileştirme Görevi B\"", 80, 40
                return "s1|echo orchestrator-demo", 50, 10

            def get_model_info(self) -> dict:
                return {"name": "stub", "provider": "local"}

            def stream_response(self, prompt: str, **kwargs):
                text, _, _ = self.generate_response(prompt, **kwargs)
                yield text

            def chat_completion(self, messages: list[dict], **kwargs) -> tuple[str, int, int]:
                return self.generate_response(messages[-1]["content"] if messages else "", **kwargs)

        llm = _StubLLM()
    else:
        from core.llm_router import LLMRouter

        llm = LLMRouter().get()

    orch = Orchestrator(llm)

    if args.action == "plan_execute":
        planned = orch.plan(args.goal)
        executed = orch.execute_plan(planned)
        print(
            json.dumps(
                {
                    "planned": [s.__dict__ for s in planned],
                    "execution": executed,
                    "evaluation": orch.evaluate(executed),
                },
                ensure_ascii=False,
            )
        )
    elif args.action == "run_self_improve":
        result = orch.run_self_improve()
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
