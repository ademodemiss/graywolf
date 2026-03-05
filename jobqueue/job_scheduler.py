import argparse
import json

from core.event_bus import EventBus
from core.event_types import EventTypes
from jobqueue.dead_letter_queue import get_dead_letters, push_dead_letter
from jobqueue.job_worker import run_command
from jobqueue.retry_manager import apply_backoff
from jobqueue.task_queue import ack_task, add_task, fail_task, get_task, lease_task_for_node, requeue_expired_leases

MAX_RETRIES = 3
BUS = EventBus()


def worker_pull_once(node_id: str = 'node-local') -> dict:
    requeue_expired_leases()
    task = lease_task_for_node(node_id)
    if not task:
        return {'status': 'idle', 'message': 'no_pending_tasks'}

    result = run_command(task['command'])
    attempts = int(task.get('attempts', 1))

    if result.get('status') == 'success' and int(result.get('log', {}).get('exit_code', 0)) == 0:
        ack_task(task['task_id'], node_id, result.get('stdout', ''))
        return {'status': 'ok', 'task_id': task['task_id'], 'node': node_id, 'attempts': attempts}

    if attempts >= int(task.get('max_retry', MAX_RETRIES)):
        fail_task(task['task_id'], node_id, reason='max_retries_exceeded')
        dlq = push_dead_letter(task, reason='max_retries_exceeded')
        return {'status': 'failed_to_dead_letter', 'task_id': task['task_id'], 'attempts': attempts, 'dead_letter': dlq}

    apply_backoff(attempts)
    # put back into queue by expiring lock immediately
    t = get_task(task['task_id'])
    if t:
        t['locked_at'] = '1970-01-01T00:00:00+00:00'
    requeue_expired_leases()
    BUS.publish(EventTypes.TASK_FAILED, {'task_id': task['task_id'], 'reason': 'retry_scheduled'})
    return {'status': 'retry_scheduled', 'task_id': task['task_id'], 'attempts': attempts}


def run_forced_failure_test() -> dict:
    task = add_task("python3 -c \"import sys; sys.exit(1)\"", lease_timeout=1, max_retry=3)
    history = []
    for _ in range(5):
        out = worker_pull_once('node-local')
        history.append(out)
        if out.get('status') in {'failed_to_dead_letter', 'idle'}:
            break
    return {
        'status': 'ok',
        'test': 'forced_failure_retry_dead_letter',
        'task_id': task['task_id'],
        'history': history,
        'dead_letter_count': len(get_dead_letters()),
    }


def main():
    p = argparse.ArgumentParser(description='GrayWolf Job Scheduler')
    p.add_argument('--task')
    p.add_argument('--node-id', default='node-local')
    p.add_argument('--test', action='store_true')
    args = p.parse_args()

    if args.test:
        print(json.dumps(run_forced_failure_test(), ensure_ascii=False))
        return

    if args.task:
        created = add_task(args.task)
        print(json.dumps({'queued': created}, ensure_ascii=False))

    print(json.dumps(worker_pull_once(args.node_id), ensure_ascii=False))


if __name__ == '__main__':
    main()
