import datetime
import json
import uuid

from jobqueue.queue_storage import load_tasks, save_tasks


def add_task(command: str) -> dict:
    tasks = load_tasks()
    task = {
        'task_id': str(uuid.uuid4()),
        'command': command,
        'status': 'pending',
        'node': None,
        'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    tasks.append(task)
    save_tasks(tasks)
    return task


def get_next_task() -> dict | None:
    tasks = load_tasks()
    for t in tasks:
        if t.get('status') == 'pending':
            t['status'] = 'running'
            save_tasks(tasks)
            return t
    return None


def update_task(task_id: str, status: str, node: str | None = None):
    tasks = load_tasks()
    for t in tasks:
        if t.get('task_id') == task_id:
            t['status'] = status
            if node is not None:
                t['node'] = node
            break
    save_tasks(tasks)


def remove_task(task_id: str):
    tasks = load_tasks()
    tasks = [t for t in tasks if t.get('task_id') != task_id]
    save_tasks(tasks)


if __name__ == '__main__':
    print(json.dumps(add_task('echo queue-demo'), ensure_ascii=False))
