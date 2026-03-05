import json
import time

from jobqueue.job_scheduler import worker_pull_once
from jobqueue.queue_storage import save_tasks
from jobqueue.task_queue import add_task, get_task, lease_task_for_node, requeue_expired_leases


def run_test() -> dict:
    # isolate test state
    save_tasks([])
    task = add_task("echo recovered-by-nodeB", lease_timeout=1)

    # nodeA pulls and 'crashes' (no ack/fail call)
    leased = lease_task_for_node('nodeA')
    crashed_task_id = leased['task_id'] if leased else None

    time.sleep(1.2)
    rep = requeue_expired_leases()

    # nodeB pulls and completes
    nodeb = worker_pull_once('nodeB')
    final = get_task(task['task_id'])

    return {
        'status': 'ok',
        'task_id': task['task_id'],
        'nodeA_leased_task': crashed_task_id,
        'requeue': rep,
        'nodeB_result': nodeb,
        'final_status': final.get('status') if final else None,
        'final_node': final.get('node') if final else None,
        'lease_fields': {
            'locked_by': final.get('locked_by') if final else None,
            'locked_at': final.get('locked_at') if final else None,
            'lease_timeout': final.get('lease_timeout') if final else None,
        },
    }


if __name__ == '__main__':
    print(json.dumps(run_test(), ensure_ascii=False))
