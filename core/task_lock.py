import argparse
import json
import os
import time
from pathlib import Path

LOCK_DIR = Path('/home/adem/graywolf/memory/task_locks')
REPORT = Path('/home/adem/graywolf/reports/task_locking_report.json')


def _lock_path(task_id: str) -> Path:
    return LOCK_DIR / f'{task_id}.lock'


def acquire_lock(task_id: str, owner: str, stale_seconds: int = 1800) -> dict:
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    p = _lock_path(task_id)
    now = int(time.time())

    if p.exists():
        try:
            data = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            data = {'owner': 'unknown', 'ts': 0}
        age = now - int(data.get('ts', 0))
        if age > stale_seconds:
            p.unlink(missing_ok=True)
        else:
            return {'ok': False, 'lock_acquired': False, 'lock_owner': data.get('owner'), 'reason': 'lock_exists', 'age_sec': age}

    fd = os.open(str(p), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(json.dumps({'owner': owner, 'ts': now}, ensure_ascii=False))
    return {'ok': True, 'lock_acquired': True, 'lock_owner': owner, 'reason': 'acquired'}


def release_lock(task_id: str, owner: str) -> dict:
    p = _lock_path(task_id)
    if not p.exists():
        return {'ok': True, 'released': False, 'reason': 'missing'}
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        data = {'owner': owner}
    if data.get('owner') != owner:
        return {'ok': False, 'released': False, 'reason': 'owner_mismatch', 'lock_owner': data.get('owner')}
    p.unlink(missing_ok=True)
    return {'ok': True, 'released': True}


def run_test() -> dict:
    task_id = 'TASK-LOCK-001'
    owner1 = 'runner-A'
    owner2 = 'runner-B'

    a1 = acquire_lock(task_id, owner1, stale_seconds=5)
    a2 = acquire_lock(task_id, owner2, stale_seconds=5)
    r1 = release_lock(task_id, owner1)
    a3 = acquire_lock(task_id, owner2, stale_seconds=5)
    r2 = release_lock(task_id, owner2)

    out = {
        'status': 'ok' if a1.get('lock_acquired') and not a2.get('lock_acquired') and a3.get('lock_acquired') else 'failed',
        'lock_owner': owner1,
        'lock_acquired': a1.get('lock_acquired'),
        'second_attempt_blocked': not a2.get('lock_acquired'),
        'stale_lock_policy': 'age > stale_seconds => purge and reacquire',
        'steps': {'first': a1, 'second': a2, 'release1': r1, 'third': a3, 'release2': r2},
    }
    REPORT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['artifact'] = str(REPORT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    p.add_argument('--task-id', default='TASK-LOCK-001')
    p.add_argument('--owner', default='runner')
    p.add_argument('--acquire', action='store_true')
    p.add_argument('--release', action='store_true')
    p.add_argument('--stale-seconds', type=int, default=1800)
    args = p.parse_args()

    if args.test:
        print(json.dumps(run_test(), ensure_ascii=False))
    elif args.acquire:
        print(json.dumps(acquire_lock(args.task_id, args.owner, stale_seconds=args.stale_seconds), ensure_ascii=False))
    elif args.release:
        print(json.dumps(release_lock(args.task_id, args.owner), ensure_ascii=False))
    else:
        print(json.dumps({'status': 'idle'}, ensure_ascii=False))
