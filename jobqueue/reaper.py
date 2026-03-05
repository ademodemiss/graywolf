import argparse
import datetime
import json
import uuid

from jobqueue.queue_storage import load_tasks, save_tasks


def reap_timeouts(timeout_minutes: int = 15) -> dict:
    tasks = load_tasks()
    now = datetime.datetime.now(datetime.timezone.utc)
    reaped = 0

    for t in tasks:
        if t.get('status') != 'running':
            continue
        started_at = t.get('started_at')
        if not started_at:
            continue
        try:
            st = datetime.datetime.fromisoformat(started_at.replace('Z', '+00:00'))
        except Exception:
            continue
        if (now - st).total_seconds() >= timeout_minutes * 60:
            t['status'] = 'failed'
            t['reason'] = 'timeout_reaped'
            t['updated_at'] = now.isoformat()
            reaped += 1

    save_tasks(tasks)
    return {'status': 'ok', 'reaped': reaped, 'timeout_minutes': timeout_minutes}


def _seed_running_old(minutes_ago: int = 20) -> dict:
    tasks = load_tasks()
    ts = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=minutes_ago)).isoformat()
    task = {
        'task_id': str(uuid.uuid4()),
        'command': 'echo stale-running',
        'status': 'running',
        'node': 'node-local',
        'attempts': 1,
        'created_at': ts,
        'started_at': ts,
        'updated_at': ts,
        'reason': None,
    }
    tasks.append(task)
    save_tasks(tasks)
    return task


def main():
    p = argparse.ArgumentParser(description='GrayWolf Jobqueue Reaper')
    p.add_argument('--timeout-minutes', type=int, default=15)
    p.add_argument('--test', action='store_true')
    args = p.parse_args()

    if args.test:
        seeded = _seed_running_old(20)
        out = reap_timeouts(args.timeout_minutes)
        print(json.dumps({'seeded': seeded['task_id'], **out}, ensure_ascii=False))
        return

    print(json.dumps(reap_timeouts(args.timeout_minutes), ensure_ascii=False))


if __name__ == '__main__':
    main()
