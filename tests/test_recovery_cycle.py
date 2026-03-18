import unittest
from unittest.mock import patch

from infra import incident_response


class RecoveryCycleTests(unittest.TestCase):
    def test_evaluate_metrics_classifies_high_retry(self):
        metrics = {
            'retry_rate': 0.5,
            'dead_letter_rate': 0.12,
            'queue_depth': 60,
            'active_nodes': 1,
        }
        incidents = incident_response.evaluate_metrics(metrics)
        self.assertIn('retry_rate_high', incidents)
        self.assertIn('dead_letter_growth', incidents)
        self.assertIn('queue_depth_high', incidents)

    def test_select_node_for_restart_prefers_most_loaded(self):
        nodes = [
            {'node_id': 'node-a', 'status': 'running', 'active_tasks': 2},
            {'node_id': 'node-b', 'status': 'running', 'active_tasks': 10},
            {'node_id': 'node-c', 'status': 'idle', 'active_tasks': 15},
        ]
        candidate = incident_response._select_node_for_restart(nodes)
        self.assertEqual(candidate['node_id'], 'node-b')

    @patch('infra.incident_response.emit_alert')
    @patch('infra.incident_response.update_node')
    @patch('infra.incident_response.get_node')
    @patch('infra.incident_response.list_nodes')
    def test_run_recovery_cycle_with_restart(self, list_nodes, get_node, update_node, emit_alert):
        list_nodes.return_value = [
            {'node_id': 'node-1', 'status': 'running', 'active_tasks': 5}
        ]
        get_node.return_value = {'node_id': 'node-1', 'status': 'running'}
        update_node.return_value = {'node_id': 'node-1', 'status': 'restarting'}

        metrics = {
            'retry_rate': 0.4,
            'dead_letter_rate': 0.1,
            'queue_depth': 50,
            'active_nodes': 1,
        }
        summary = incident_response.run_recovery_cycle(metrics)
        self.assertEqual(summary['candidate_node'], 'node-1')
        self.assertEqual(summary['actions'][0]['action'], 'restart_scheduled')
        emit_alert.assert_called()


if __name__ == '__main__':
    unittest.main()
