import datetime
import json
import uuid

from core.event_bus import EventBus
from core.event_types import EventTypes
from jobqueue.queue_storage import load_tasks, save_tasks

BUS = EventBus()


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _parse_ts(v: str | None):
    if not v:
        return None
    try:
        return datetime.datetime.fromisoformat(v.replace('Z', '+00:00'))
    except Exception:
        return None


def add_task(command: str, lease_timeout: int = 60, max_retry: int = 3) -> dict:
    tasks = load_tasks()
    now = _now()
    task = {
        'task_id': str(uuid.uuid4()),
        'command': command,
        'status': 'pending',
        'node': None,
        'attempts': 0,
        'max_retry': max_retry,
        'created_at': now,
        'started_at': None,
        'updated_at': now,
        'finished_at': None,
        'reason': None,
        'locked_by': None,
        'locked_at': None,
        'lease_timeout': lease_timeout,
    }
    tasks.append(task)
    save_tasks(tasks)
    BUS.publish(EventTypes.TASK_CREATED, {'task_id': task['task_id'], 'command': command})
    return task


def lease_task_for_node(node_id: str) -> dict | None:
    tasks = load_tasks()
    for t in tasks:
        if t.get('status') != 'pending':
            continue
        now = _now()
        t['status'] = 'running'
        t['started_at'] = now
        t['updated_at'] = now
        t['attempts'] = int(t.get('attempts', 0)) + 1
        t['locked_by'] = node_id
        t['locked_at'] = now
        t['node'] = node_id
        save_tasks(tasks)
        BUS.publish(EventTypes.TASK_LEASED, {'task_id': t['task_id'], 'node_id': node_id, 'attempts': t['attempts']})
        BUS.publish(EventTypes.TASK_STARTED, {'task_id': t['task_id'], 'node_id': node_id})
        return t
    return None


def ack_task(task_id: str, node_id: str, result: str = ''):
    tasks = load_tasks()
    for t in tasks:
        if t.get('task_id') == task_id:
            t['status'] = 'completed'
            t['updated_at'] = _now()
            t['finished_at'] = t['updated_at']
            t['result'] = result
            t['locked_by'] = None
            t['locked_at'] = None
            t['node'] = node_id
            save_tasks(tasks)
            BUS.publish(EventTypes.TASK_COMPLETED, {'task_id': task_id, 'node_id': node_id})
            return


def fail_task(task_id: str, node_id: str, reason: str = 'failed'):
    tasks = load_tasks()
    for t in tasks:
        if t.get('task_id') == task_id:
            t['status'] = 'failed'
            t['updated_at'] = _now()
            t['finished_at'] = t['updated_at']
            t['reason'] = reason
            t['locked_by'] = None
            t['locked_at'] = None
            t['node'] = node_id
            save_tasks(tasks)
            BUS.publish(EventTypes.TASK_FAILED, {'task_id': task_id, 'node_id': node_id, 'reason': reason})
            return


def requeue_expired_leases() -> dict:
    tasks = load_tasks()
    now = datetime.datetime.now(datetime.timezone.utc)
    requeued = 0
    for t in tasks:
        if t.get('status') != 'running' or not t.get('locked_at'):
            continue
        locked_at = _parse_ts(t.get('locked_at'))
        if not locked_at:
            continue
        lease_timeout = int(t.get('lease_timeout', 60) or 60)
        if (now - locked_at).total_seconds() >= lease_timeout:
            t['status'] = 'pending'
            t['updated_at'] = _now()
            t['reason'] = 'lease_expired_requeue'
            t['locked_by'] = None
            t['locked_at'] = None
            requeued += 1
    if requeued:
        save_tasks(tasks)
    return {'status': 'ok', 'requeued': requeued}


def get_task(task_id: str) -> dict | None:
    for t in load_tasks():
        if t.get('task_id') == task_id:
            return t
    return None


if __name__ == '__main__':
    print(json.dumps(add_task('echo queue-demo'), ensure_ascii=False))
