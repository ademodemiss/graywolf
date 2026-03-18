import unittest

from core.approval import ApprovalRequest, ApprovalState
from core.human_gate import HumanGate
from policies.shell_policy import ShellPolicy


class StubTerminalTool:
    def __init__(self):
        self.ran = []

    def run_command(self, command: str, timeout: int = 60, policy_decision=None, policy_reason=None) -> dict:
        self.ran.append((command, policy_decision))
        return {
            "status": "success",
            "stdout": f"ran {command}",
            "stderr": "",
            "log": {"cmd": command, "decision": policy_decision.value if policy_decision else ""},
        }


class StubApprovalManager:
    def __init__(self, outcome: ApprovalState = ApprovalState.GRANTED):
        self.outcome = outcome
        self.last_request: ApprovalRequest | None = None

    def evaluate_command(self, command: str, requested_by: str | None = None, category_hint: str | None = None):
        if "confirm" in command:
            request = ApprovalRequest("stub-req", command, "test-category")
            request.status = ApprovalState.PENDING
            self.last_request = request
            return request, "needs confirmation"
        return None, "allowed"

    def wait_for_status(self, request_id: str, target: set[ApprovalState], timeout_seconds: int = 60) -> ApprovalRequest | None:
        if not self.last_request:
            return None
        self.last_request.status = self.outcome
        return self.last_request


class HumanGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = StubTerminalTool()
        self.manager = StubApprovalManager()
        self.gate = HumanGate(
            terminal_tool=self.tool,
            approval_manager=self.manager,
            policy=ShellPolicy(),
            confirmation_timeout=1,
        )

    def test_allows_safe_command(self):
        result = self.gate.execute_command("echo hello")
        self.assertEqual(result["status"], "success")
        self.assertIsNone(result.get("approval_request"))
        self.assertEqual(len(self.tool.ran), 1)

    def test_runs_after_approval(self):
        self.manager.outcome = ApprovalState.GRANTED
        result = self.gate.execute_command("confirm risky step")
        self.assertEqual(result["status"], "success")
        self.assertIsNotNone(result.get("approval_request"))
        self.assertEqual(result["approval_request"]["status"], ApprovalState.GRANTED.value)
        self.assertEqual(len(self.tool.ran), 1)

    def test_handles_denied(self):
        self.manager.outcome = ApprovalState.DENIED
        result = self.gate.execute_command("confirm risky step")
        self.assertEqual(result["status"], "denied")
        self.assertEqual(len(self.tool.ran), 0)


if __name__ == "__main__":
    unittest.main()
