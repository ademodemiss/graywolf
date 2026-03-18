import json
from datetime import datetime, timezone

from cluster.node_manager import list_nodes
from jobqueue.dead_letter_queue import get_dead_letters
from jobqueue.queue_storage import load_tasks


def _iso_to_dt(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except Exception:
        return None


def collect_metrics() -> dict:
    tasks = load_tasks()
    dead = get_dead_letters()
    nodes = list_nodes()

    now = datetime.now(timezone.utc)
    queue_depth = sum(1 for t in tasks if t.get('status') in {'pending', 'running'})

    latencies = []
    runtimes = []
    retries = 0
    total = max(len(tasks), 1)
    failed = sum(1 for t in tasks if t.get('status') == 'failed')
    running = sum(1 for t in tasks if t.get('status') == 'running')
    attempts_total = sum(int(t.get('attempts', 0)) for t in tasks)

    for t in tasks:
        retries += max(int(t.get('attempts', 0)) - 1, 0)
        q = _iso_to_dt(t.get('created_at'))
        s = _iso_to_dt(t.get('started_at'))
        f = _iso_to_dt(t.get('updated_at'))
        if q and s:
            latencies.append(int((s - q).total_seconds() * 1000))
        if s and f and t.get('status') in {'completed', 'failed'}:
            runtimes.append(int((f - s).total_seconds() * 1000))

    queue_latency_ms = int(sum(latencies) / len(latencies)) if latencies else 0
    avg_task_runtime_ms = int(sum(runtimes) / len(runtimes)) if runtimes else 0
    retry_rate = round(retries / total, 4)
    dead_letter_count = len(dead)
    dead_letter_rate = round(dead_letter_count / total, 4)
    failure_rate = round(failed / total, 4)
    attempt_rate = round(attempts_total / total, 4)
    unhappy_tasks = failed + dead_letter_count

    active_nodes = sum(1 for n in nodes if str(n.get('status', '')).lower() == 'running')
    active_tasks = sum(int(n.get('active_tasks', 0) or 0) for n in nodes)

    scheduler_delay_ms = 0
    if tasks:
        oldest_pending = None
        for t in tasks:
            if t.get('status') != 'pending':
                continue
            c = _iso_to_dt(t.get('created_at'))
            if c and (oldest_pending is None or c < oldest_pending):
                oldest_pending = c
        if oldest_pending:
            scheduler_delay_ms = int((now - oldest_pending).total_seconds() * 1000)

    node_idle_time = 0

    return {
        'queue_depth': queue_depth,
        'queue_latency_ms': queue_latency_ms,
        'avg_task_runtime_ms': avg_task_runtime_ms,
        'retry_rate': retry_rate,
        'failure_rate': failure_rate,
        'dead_letter_rate': dead_letter_rate,
        'dead_letter_count': dead_letter_count,
        'unhappy_tasks': unhappy_tasks,
        'attempt_rate': attempt_rate,
        'node_idle_time': node_idle_time,
        'scheduler_delay_ms': scheduler_delay_ms,
        'active_nodes': active_nodes,
        'active_tasks': active_tasks,
        'running_tasks': running,
        'failed_tasks': failed,
    }


if __name__ == '__main__':
    print(json.dumps(collect_metrics(), ensure_ascii=False))
