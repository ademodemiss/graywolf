import datetime
import json
from pathlib import Path
from typing import Iterable

from cluster.node_manager import get_node, list_nodes, update_node
from monitor.alert import emit_alert

LOG_DIR = Path('/home/adem/graywolf/logs')
INCIDENT_LOG = LOG_DIR / 'incident_response.log'

THRESHOLDS = {
    'retry_rate': 0.25,
    'dead_letter_rate': 0.08,
    'queue_depth': 40,
}


def _write_entry(entry: dict):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(INCIDENT_LOG, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + '\n')


def _current_ts() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def evaluate_metrics(metrics: dict) -> list[str]:
    incidents = []
    if metrics.get('retry_rate', 0) >= THRESHOLDS['retry_rate']:
        incidents.append('retry_rate_high')
    if metrics.get('dead_letter_rate', 0) >= THRESHOLDS['dead_letter_rate']:
        incidents.append('dead_letter_growth')
    if metrics.get('queue_depth', 0) >= THRESHOLDS['queue_depth']:
        incidents.append('queue_depth_high')
    if metrics.get('active_nodes', 0) == 0:
        incidents.append('no_active_nodes')
    return incidents


def _select_node_for_restart(nodes: Iterable[dict]) -> dict | None:
    running_nodes = [n for n in nodes if str(n.get('status', '')).lower() == 'running']
    candidates = running_nodes or list(nodes)
    if not candidates:
        return None
    return max(candidates, key=lambda n: int(n.get('active_tasks', 0) or 0))


def _record_action(action: str, detail: str, node_id: str | None = None) -> dict:
    entry = {
        'ts': _current_ts(),
        'action': action,
        'node_id': node_id,
        'detail': detail,
    }
    _write_entry(entry)
    return entry


def restart_node(node_id: str, reason: str) -> dict:
    node = get_node(node_id)
    if not node:
        detail = f'node {node_id} not registered'
        emit_alert('NODE_RESTART_FAILED', detail)
        return _record_action('restart_failed', detail, node_id)

    next_restarts = int(node.get('restarts', 0) or 0) + 1
    payload = {
        'status': 'restarting',
        'last_incident': reason,
        'last_incident_at': _current_ts(),
        'restarts': next_restarts,
    }
    updated = update_node(node_id, payload)
    detail = f'restart scheduled for {node_id} (reason={reason})'
    emit_alert('NODE_RESTART', detail)
    return _record_action('restart_scheduled', detail, node_id)


def run_recovery_cycle(metrics: dict | None = None) -> dict:
    from monitor.metrics_collector import collect_metrics

    m = metrics or collect_metrics()
    incidents = evaluate_metrics(m)
    nodes = list_nodes()

    summary = {
        'metrics': m,
        'incidents': incidents,
        'actions': [],
        'candidate_node': None,
    }

    if not nodes:
        detail = 'no registered nodes available for recovery'
        emit_alert('NO_NODES_AVAILABLE', detail)
        summary['actions'].append({'status': 'no_nodes', 'detail': detail})
        return summary

    candidate = _select_node_for_restart(nodes)
    summary['candidate_node'] = candidate.get('node_id') if candidate else None

    if incidents and candidate:
        action = restart_node(candidate['node_id'], incidents[0])
        summary['actions'].append(action)
    else:
        summary['actions'].append({'status': 'idle', 'detail': 'no incidents detected or no candidate'})

    return summary


def run_test() -> dict:
    fake_metrics = {
        'retry_rate': 0.4,
        'dead_letter_rate': 0.1,
        'queue_depth': 50,
        'active_nodes': 0,
    }
    return run_recovery_cycle(fake_metrics)


if __name__ == '__main__':
    print(json.dumps(run_test(), ensure_ascii=False))
