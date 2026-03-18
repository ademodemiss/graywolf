"""Workflow komutlarını ApprovalManager üzerinden gate eden yardımcı."""
from __future__ import annotations

from typing import Iterable

from core.approval import ApprovalManager, ApprovalRequest, ApprovalState
from policies.shell_policy import PolicyDecision, ShellPolicy
from tools.terminal_tool import TerminalTool


class HumanGate:
    def __init__(
        self,
        confirmation_timeout: int = 60,
        terminal_tool: TerminalTool | None = None,
        approval_manager: ApprovalManager | None = None,
        policy: ShellPolicy | None = None,
        requested_by: str = "workflow_engine",
        log_dir: str = "/home/adem/graywolf/logs",
    ) -> None:
        policy = policy or ShellPolicy()
        self.requested_by = requested_by
        self.confirmation_timeout = confirmation_timeout
        self.tool = terminal_tool or TerminalTool(policy_engine=policy, log_dir=log_dir)
        self.manager = approval_manager or ApprovalManager(policy=policy)

    def execute_command(self, command: str, step_name: str | None = None, timeout: int = 60) -> dict:
        payload_hint = step_name or "workflow_step"
        request, reason = self.manager.evaluate_command(
            command,
            requested_by=self.requested_by,
            category_hint=payload_hint,
        )
        if not request:
            result = self.tool.run_command(
                command,
                timeout=timeout,
                policy_decision=PolicyDecision.ALLOW,
                policy_reason=reason,
            )
            result["approval_request"] = None
            return result

        if request.status == ApprovalState.GRANTED:
            return self._run_with_approval(command, request, timeout, reason)

        if request.status in {ApprovalState.DENIED, ApprovalState.SKIPPED}:
            return self._blocked_result(request)

        waited = self.manager.wait_for_status(
            request.request_id,
            {ApprovalState.GRANTED, ApprovalState.DENIED, ApprovalState.SKIPPED},
            timeout_seconds=self.confirmation_timeout,
        )
        if not waited:
            return {
                "status": "blocked",
                "stdout": "",
                "stderr": "Approval wait timed out.",
                "approval_request": request.to_payload(),
            }

        if waited.status == ApprovalState.GRANTED:
            return self._run_with_approval(command, waited, timeout, "Approved")

        return self._blocked_result(waited)

    def _run_with_approval(self, command: str, request: ApprovalRequest, timeout: int, reason: str) -> dict:
        result = self.tool.run_command(
            command,
            timeout=timeout,
            policy_decision=PolicyDecision.ALLOW,
            policy_reason=reason,
        )
        result["approval_request"] = request.to_payload()
        return result

    def _blocked_result(self, request: ApprovalRequest) -> dict:
        status = "denied" if request.status == ApprovalState.DENIED else "skipped"
        return {
            "status": status,
            "stdout": "",
            "stderr": f"Command {status} via approval workflow.",
            "approval_request": request.to_payload(),
        }
