import unittest
from unittest.mock import mock_open, patch

from core.event_types import EventTypes
from monitor.recovery_dispatcher import RecoveryDispatcher


class FakeBus:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type, handler):
        self.subscribers.setdefault(event_type, []).append(handler)

    def trigger(self, event_type, payload):
        event = {'type': event_type, 'payload': payload}
        for handler in self.subscribers.get(event_type, []):
            handler(event)


class RecoveryDispatcherTests(unittest.TestCase):
    def test_dispatcher_triggers_recovery_on_task_failure(self):
        fake_bus = FakeBus()
        with patch('monitor.recovery_dispatcher.collect_metrics', return_value={'queue_depth': 3}) as mock_metrics, \
             patch('monitor.recovery_dispatcher.run_recovery_cycle', return_value={'status': 'recovered'}) as mock_recovery, \
             patch('monitor.recovery_dispatcher.open', mock_open()):
            dispatcher = RecoveryDispatcher(buses=[fake_bus], cooldown_seconds=0)
            fake_bus.trigger(EventTypes.TASK_FAILED, {'task_id': 't-123'})

        mock_metrics.assert_called_once()
        mock_recovery.assert_called_once_with({'queue_depth': 3})

    def test_dispatcher_skips_run_when_cooldown(self):
        fake_bus = FakeBus()
        with patch('monitor.recovery_dispatcher.collect_metrics') as mock_metrics, \
             patch('monitor.recovery_dispatcher.run_recovery_cycle') as mock_recovery, \
             patch('monitor.recovery_dispatcher.open', mock_open()):
            mock_metrics.return_value = {'queue_depth': 2}
            mock_recovery.return_value = {'status': 'ok'}
            dispatcher = RecoveryDispatcher(buses=[fake_bus], cooldown_seconds=10)
            dispatcher._last_run_ts = 0
            fake_bus.trigger(EventTypes.TASK_FAILED, {'task_id': 't-1'})
            fake_bus.trigger(EventTypes.TASK_FAILED, {'task_id': 't-2'})

        mock_metrics.assert_called_once()
        mock_recovery.assert_called_once()


if __name__ == '__main__':
    unittest.main()
