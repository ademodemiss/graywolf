import argparse
import json
import time

from jobqueue.task_queue import add_task, get_task, lease_task_for_node, requeue_expired_leases


def run_test() -> dict:
    task = add_task('echo lease-recovery', lease_timeout=1)
    leased = lease_task_for_node('nodeA')
    time.sleep(1.2)
    rep = requeue_expired_leases()
    after = get_task(task['task_id'])
    return {
        'status': 'ok',
        'task_id': task['task_id'],
        'leased_by': leased.get('locked_by') if leased else None,
        'reaper': rep,
        'after_status': after.get('status') if after else None,
    }


def main():
    p = argparse.ArgumentParser(description='GrayWolf Lease Reaper')
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    if args.test:
        print(json.dumps(run_test(), ensure_ascii=False))
        return
    print(json.dumps(requeue_expired_leases(), ensure_ascii=False))


if __name__ == '__main__':
    main()
