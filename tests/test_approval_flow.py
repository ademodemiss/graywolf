import unittest
from typing import Callable

from core.approval import ApprovalManager, ApprovalState
from core.event_types import EventTypes
from policies.shell_policy import ShellPolicy


class FakeBus:
    def __init__(self):
        self.subscribers: dict[str, list[Callable[[dict], None]]] = {}
        self.events: list[tuple[str, dict]] = []

    def subscribe(self, event_type: str, handler: Callable[[dict], None]):
        self.subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event_type: str, payload: dict):
        self.events.append((event_type, payload))
        for handler in self.subscribers.get(event_type, []):
            handler({"payload": payload})


class ApprovalFlowTests(unittest.TestCase):
    def setUp(self):
        self.bus = FakeBus()
        self.policy = ShellPolicy()
        self.manager = ApprovalManager(bus=self.bus, policy=self.policy)

    def test_confirm_command_creates_pending_request(self):
        request, _ = self.manager.evaluate_command("mv /tmp/a /tmp/b", requested_by="agent")
        self.assertIsNotNone(request)
        self.assertEqual(request.status, ApprovalState.PENDING)
        self.assertEqual(self.bus.events[-1][0], EventTypes.APPROVAL_REQUESTED)
        self.assertEqual(self.manager.get_request(request.request_id).status, ApprovalState.PENDING)

    def test_allow_command_returns_none(self):
        request, _ = self.manager.evaluate_command("ls -l", requested_by="agent")
        self.assertIsNone(request)
        self.assertNotIn(EventTypes.APPROVAL_REQUESTED, [event for event, _ in self.bus.events])

    def test_denied_command_publishes_denial(self):
        request, _ = self.manager.evaluate_command("sudo reboot", requested_by="agent")
        self.assertEqual(request.status, ApprovalState.DENIED)
        self.assertEqual(self.bus.events[-1][0], EventTypes.APPROVAL_DENIED)
        self.assertEqual(self.manager.get_request(request.request_id).status, ApprovalState.DENIED)

    def test_auto_grant_allows_commands(self):
        manager = ApprovalManager(bus=self.bus, policy=self.policy, auto_grant_allow=True)
        request, _ = manager.evaluate_command("ls -l", requested_by="agent")
        self.assertIsNotNone(request)
        self.assertEqual(request.status, ApprovalState.GRANTED)
        self.assertEqual(self.bus.events[-1][0], EventTypes.APPROVAL_GRANTED)

    def test_external_grant_updates_state(self):
        request, _ = self.manager.evaluate_command("mv /tmp/a /tmp/b", requested_by="agent")
        self.bus.publish(EventTypes.APPROVAL_GRANTED, request.to_payload())
        self.assertEqual(self.manager.get_request(request.request_id).status, ApprovalState.GRANTED)


if __name__ == "__main__":
    unittest.main()
