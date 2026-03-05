import json
from jobqueue.queue_storage import load_tasks


def get_status() -> dict:
    tasks = load_tasks()
    counters = {'pending': 0, 'running': 0, 'completed': 0, 'failed': 0}
    for t in tasks:
        s = t.get('status', 'pending')
        counters[s] = counters.get(s, 0) + 1
    return {'status': 'ok', 'counts': counters, 'total': len(tasks)}


if __name__ == '__main__':
    print(json.dumps(get_status(), ensure_ascii=False))
