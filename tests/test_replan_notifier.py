import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.event_bus import EventBus
from core.event_types import EventTypes
from monitor.replan_notifier import ReplanNotifier


class ReplanNotifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.log_dir = tempfile.mkdtemp(prefix="replan-log-")
        self.bus = EventBus()
        self.notifier = ReplanNotifier(bus=self.bus, log_dir=self.log_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.log_dir, ignore_errors=True)

    @patch("monitor.replan_notifier.send_telegram_message")
    def test_ready_event_sends_summary(self, mock_send):
        payload = {
            "workflow_name": "orchestrator-plan",
            "hint": "adjust_permissions",
            "original_error": {"stderr": "Permission denied", "stderr_snippet": "perm"},
            "new_plan": [{"name": "inspect", "cmd": "echo inspect"}],
            "info": {"status": "replan_ready"},
        }
        self.bus.publish(EventTypes.REPLAN_READY, payload)

        mock_send.assert_called_once()
        message = mock_send.call_args[0][0]
        self.assertIn("workflow=orchestrator-plan", message)
        self.assertIn("Yeni plan uzunluğu: 1 adım", message)

        log_path = Path(self.log_dir) / "replan_notifier.log"
        self.assertTrue(log_path.exists())

    @patch("monitor.replan_notifier.send_telegram_message")
    def test_executed_event_reports_results(self, mock_send):
        payload = {
            "workflow_name": "orchestrator-plan",
            "replan_info": {"hint": "retry"},
            "replan_result": {
                "status": "completed",
                "results": [
                    {"name": "replan_inspect", "status": "success"},
                    {"name": "replan_retry", "status": "success"},
                ],
            },
        }
        self.bus.publish(EventTypes.REPLAN_EXECUTED, payload)

        mock_send.assert_called_once()
        message = mock_send.call_args[0][0]
        self.assertIn("Görev durumu: completed", message)
        self.assertIn("Adım sonuçları: replan_inspect:success | replan_retry:success", message)

        log_path = Path(self.log_dir) / "replan_notifier.log"
        self.assertTrue(log_path.exists())


if __name__ == "__main__":
    unittest.main()
