import argparse
import json
import time
from dataclasses import dataclass

from adapters.llm.llm_adapter import LLMAdapter
from core.llm_router import LLMRouter
from workflows.runner import run_workflow


@dataclass
class OrchestratorStep:
    name: str
    instruction: str


class Orchestrator:
    """Faz 2: plan -> tool -> evaluate (+ retry/backoff + error classification)"""

    def __init__(self, llm: LLMAdapter, max_retries: int = 2, backoff_seconds: float = 1.0):
        self.llm = llm
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

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
            "Sadece komut yaz, açıklama yazma.\n"
            f"Goal: {goal}"
        )

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                raw = self.llm.generate_response(prompt)
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
            instruction = instruction.strip()
            if name and instruction:
                steps.append(OrchestratorStep(name=name, instruction=instruction))
        return steps[:3]

    def execute_plan(self, steps: list[OrchestratorStep]) -> dict:
        workflow = {
            "name": "orchestrator-plan",
            "steps": [{"name": s.name, "cmd": s.instruction} for s in steps],
        }
        return run_workflow(workflow)

    def evaluate(self, execution_result: dict) -> str:
        statuses = [f"{r['name']}:{r['status']}" for r in execution_result.get("results", [])]
        return " | ".join(statuses) if statuses else "no-steps"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GrayWolf Orchestrator")
    parser.add_argument("--goal", default="demo")
    parser.add_argument("--provider", choices=["router", "stub"], default="stub")
    args = parser.parse_args()

    if args.provider == "stub":

        class _StubLLM(LLMAdapter):
            def generate_response(self, prompt: str, **kwargs) -> str:
                return "s1|echo orchestrator-demo"

            def get_model_info(self) -> dict:
                return {"name": "stub", "provider": "local"}

            def stream_response(self, prompt: str, **kwargs):
                yield self.generate_response(prompt, **kwargs)

            def chat_completion(self, messages: list[dict], **kwargs) -> str:
                return self.generate_response(messages[-1]["content"] if messages else "", **kwargs)

        llm = _StubLLM()
    else:
        llm = LLMRouter().get()

    orch = Orchestrator(llm)
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
