import threading
import time
import unittest

from core.approval import ApprovalManager, ApprovalState
from core.event_types import EventTypes


class ApprovalWaitTests(unittest.TestCase):
    def test_wait_for_granted(self):
        manager = ApprovalManager()
        request, _ = manager.evaluate_command("mv /tmp/a /tmp/b", requested_by="tester")
        self.assertIsNotNone(request)
        self.assertEqual(request.status, ApprovalState.PENDING)

        def grant():
            time.sleep(0.05)
            manager.bus.publish(EventTypes.APPROVAL_GRANTED, request.to_payload())

        threading.Thread(target=grant, daemon=True).start()
        final = manager.wait_for_status(request.request_id, {ApprovalState.GRANTED}, timeout_seconds=2)
        self.assertIsNotNone(final)
        self.assertEqual(final.status, ApprovalState.GRANTED)

    def test_wait_for_denied(self):
        manager = ApprovalManager()
        request, _ = manager.evaluate_command("mv /tmp/a /tmp/b", requested_by="tester")
        self.assertIsNotNone(request)

        def deny():
            time.sleep(0.05)
            manager.bus.publish(EventTypes.APPROVAL_DENIED, request.to_payload())

        threading.Thread(target=deny, daemon=True).start()
        final = manager.wait_for_status(request.request_id, {ApprovalState.DENIED}, timeout_seconds=2)
        self.assertIsNotNone(final)
        self.assertEqual(final.status, ApprovalState.DENIED)


if __name__ == "__main__":
    unittest.main()
