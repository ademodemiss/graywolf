import unittest

from core.event_bus import EventBus
from core.event_types import EventTypes
from monitor.approval_callback_router import ApprovalCallbackRouter


class ApprovalCallbackRouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bus = EventBus()
        self.router = ApprovalCallbackRouter(bus=self.bus)
        self.events = []

        def capture(evt: dict):
            self.events.append(evt)

        self.bus.subscribe(EventTypes.APPROVAL_GRANTED, capture)
        self.bus.subscribe(EventTypes.APPROVAL_DENIED, capture)

    def test_grant_publishes_event(self):
        result = self.router.handle_callback("approval.grant:req-42", actor="tester")
        self.assertEqual(result["event"], EventTypes.APPROVAL_GRANTED)
        self.assertEqual(result["status"], "granted")
        self.assertEqual(len(self.events), 1)
        payload = self.events[0]["payload"]
        self.assertEqual(payload["request_id"], "req-42")
        self.assertEqual(payload["status"], "granted")
        self.assertEqual(payload["actor"], "tester")

    def test_deny_publishes_event(self):
        self.router.handle_callback("approval.deny:req-777")
        self.assertEqual(len(self.events), 1)
        self.assertEqual(self.events[0]["type"], EventTypes.APPROVAL_DENIED)
        self.assertEqual(self.events[0]["payload"]["status"], "denied")

    def test_invalid_callback_raises(self):
        with self.assertRaises(ValueError):
            self.router.handle_callback("invalid::data")


if __name__ == "__main__":
    unittest.main()
