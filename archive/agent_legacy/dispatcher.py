"""Agent dispatcher: decomposed adımları çalıştıran iskelet."""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List

from agent.task_decomposer import decompose_plan, plan_summary_from_command
from agent.tool_handlers import (
    CodeHandler,
    ExcelHandler,
    FileHandler,
    MailHandler,
    ReportHandler,
)
from core.approval import ApprovalManager
from core.human_gate import HumanGate
from memory.lesson_manager import LessonManager
from memory.memory_store import store_memory
from monitor.approval_notifier import ApprovalNotifier
from policies.shell_policy import ShellPolicy
from tools.terminal_tool import TerminalTool
from tools.tool_guard import ToolGuard

ToolHandler = Callable[[Dict], Dict]


def _mock_tool_executor(step: Dict) -> Dict:
    return {
        "status": "simulated",
        "tool": step["tool"],
        "description": step.get("description"),
        "details": "Bu adım halen simülasyon, gerçek tool entegrasyonu Phase B'de yapılacak.",
        "step_id": step.get("id"),
    }


class Dispatcher:
    def __init__(self):
        self.shell_policy = ShellPolicy()
        self.log_dir = Path("/home/adem/graywolf/logs")
        self.memory_dir = Path("/home/adem/graywolf/memory")
        self.workspace_memory = Path("/home/adem/.openclaw/workspace/memory")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.workspace_memory.mkdir(parents=True, exist_ok=True)

        self.tool_guard = ToolGuard(policy=self.shell_policy, log_dir=str(self.log_dir))
        self.approval_manager = ApprovalManager(policy=self.shell_policy)
        self.approval_notifier = ApprovalNotifier()
        self.human_gate = HumanGate(
            policy=self.shell_policy,
            approval_manager=self.approval_manager,
            confirmation_timeout=90,
            terminal_tool=TerminalTool(policy_engine=self.shell_policy, log_dir=str(self.log_dir)),
            requested_by="dispatcher",
        )
        self.lesson_manager = LessonManager(memory_dir=str(self.memory_dir))
        self.pending_log = self.memory_dir / "pending_approvals.jsonl"
        self._pending_seen: set[str] = set()
        self._current_goal: str | None = None

        self.file_handler = FileHandler()
        self.code_handler = CodeHandler()
        self.excel_handler = ExcelHandler()
        self.mail_handler = MailHandler()
        self.report_handler = ReportHandler()
        self._handlers: Dict[str, ToolHandler] = {
            "terminal": self._execute_terminal,
            "file_tool": self.file_handler.execute,
            "code_tool": self.code_handler.execute,
            "excel_tool": self.excel_handler.execute,
            "mail_tool": self.mail_handler.execute,
            "report_tool": self.report_handler.execute,
            "telegram_alert": _mock_tool_executor,
        }

    def _render_terminal_command(self, step: Dict) -> str:
        if step.get("command"):
            return step["command"]
        safe_text = str(step.get("description", ""))
        safe_text = safe_text.replace('"', "'")
        return f"echo \"{safe_text}\""

    def _execute_terminal(self, step: Dict) -> Dict:
        command = self._render_terminal_command(step)
        guard_report = self.tool_guard.inspect(command)
        result = self.human_gate.execute_command(command, step_name=step.get("description"))
        log = result.get("log") or {}
        self._record_pending_approval(result.get("approval_request"), step, guard_report)
        store_memory(
            goal=self._current_goal or step.get("description", "terminal"),
            workflow=step.get("tool", "terminal"),
            result=result.get("status", "unknown"),
            error=result.get("stderr", log.get("reason", "")) or "",
            decision=guard_report.get("decision", ""),
        )
        self._record_lesson(step, command, result)
        return {
            "status": result["status"],
            "tool": "terminal",
            "description": step.get("description"),
            "command": command,
            "stdout": result.get("stdout"),
            "stderr": result.get("stderr"),
            "policy_decision": log.get("decision"),
            "policy_reason": log.get("reason"),
            "guard_severity": guard_report.get("severity"),
            "guard_reason": guard_report.get("reason"),
            "step_id": step.get("id"),
            "duration_ms": log.get("duration_ms"),
            "approval_request": result.get("approval_request"),
        }

    def _record_lesson(self, step: Dict, command: str, result: Dict) -> None:
        status = result.get("status")
        outcome = "success" if status == "success" else "failure"
        key_takeaway = f"{step.get('description', 'terminal')} -> {status}"
        context = {
            "command": command,
            "stdout": result.get("stdout"),
            "stderr": result.get("stderr"),
            "policy_reason": result.get("approval_request", {}).get("reason") if isinstance(result.get("approval_request"), dict) else None,
        }
        task_id = step.get("id") or f"step-{int(time.time() * 1000)}"
        self.lesson_manager.learn(task_id, outcome, key_takeaway, context)

    def _record_pending_approval(self, payload: Dict | None, step: Dict, guard_report: Dict) -> None:
        if not payload or payload.get("status") != "pending":
            return
        request_id = payload.get("request_id")
        if not request_id or request_id in self._pending_seen:
            return
        self._pending_seen.add(request_id)
        entry = {
            "request_id": request_id,
            "command": payload.get("command"),
            "category": payload.get("category"),
            "severity": guard_report.get("severity"),
            "reason": guard_report.get("reason"),
            "step_id": step.get("id"),
            "description": step.get("description"),
            "timestamp": payload.get("created_at") or datetime.now(timezone.utc).isoformat(),
        }
        self.pending_log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.pending_log, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        note = (
            f"{entry['timestamp']} - pending onay: {entry['command']} (id {request_id}, severity {entry['severity']})"
        )
        self._append_workspace_memory(note)

    def _append_workspace_memory(self, note: str) -> None:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        target = self.workspace_memory / f"{today}.md"
        if not target.exists():
            target.touch()
        with open(target, "a", encoding="utf-8") as handle:
            handle.write(note + "\n")

    def dispatch(self, command: str) -> Dict:
        plan_bundle = plan_summary_from_command(command)
        self._current_goal = plan_bundle["plan"]["objective"]
        execution_log: List[Dict] = []
        for step in plan_bundle["decomposed_steps"]:
            handler = self._handlers.get(step["tool"], _mock_tool_executor)
            execution = handler(step)
            execution_log.append(execution)
        self._current_goal = None
        return {
            "objective": plan_bundle["plan"]["objective"],
            "plan_summary": plan_bundle["plan"]["plan_summary"],
            "steps_executed": execution_log,
            "timestamp": time.time(),
        }


if __name__ == "__main__":
    dispatcher = Dispatcher()
    samples = [
        "Şirket sitesi yap ve deploy et",
        "Excel'deki satış tablosunu analiz et",
        "Sunucuda git pull yapıp testleri çalıştır",
    ]
    for sample in samples:
        result = dispatcher.dispatch(sample)
        print(json.dumps(result, ensure_ascii=False, indent=2))
