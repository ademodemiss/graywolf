import argparse
import json

from cluster.task_dispatcher import dispatch_task
from jobqueue.task_queue import add_task, get_next_task, update_task


def schedule_once() -> dict:
    task = get_next_task()
    if not task:
        return {'status': 'idle', 'message': 'no_pending_tasks'}

    result = dispatch_task(task['command'])
    if result.get('status') == 'ok':
        update_task(task['task_id'], 'completed', result.get('node'))
    else:
        update_task(task['task_id'], 'failed')
    return {'status': 'ok', 'task_id': task['task_id'], 'dispatch': result}


def main():
    p = argparse.ArgumentParser(description='GrayWolf Job Scheduler')
    p.add_argument('--task')
    args = p.parse_args()

    if args.task:
        created = add_task(args.task)
        print(json.dumps({'queued': created}, ensure_ascii=False))

    print(json.dumps(schedule_once(), ensure_ascii=False))


if __name__ == '__main__':
    main()
