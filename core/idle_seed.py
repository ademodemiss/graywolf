import argparse
import json
import time
from pathlib import Path

from core.task_generator import generate_task

ROADMAP = Path('/home/adem/graywolf/docs/roadmap.md')
STATE_FILE = Path('/home/adem/graywolf/memory/idle_tasks/.cooldown.json')


def _has_incomplete() -> bool:
    if not ROADMAP.exists():
        return False
    for line in ROADMAP.read_text(encoding='utf-8').splitlines():
        if line.startswith('## Phase ') and '✅' not in line:
            return True
    return False


def _load_state() -> dict:
    if not STATE_FILE.exists():
        return {'last_seed_ts': 0}
    try:
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    except Exception:
        return {'last_seed_ts': 0}


def _save_state(st: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding='utf-8')


def seed_next_batch_if_idle(batch_size: int = 5) -> dict:
    # Compatibility shim for existing agent_loop import.
    _ = batch_size
    return run_once(cooldown=900)


def run_once(cooldown: int = 900) -> dict:
    if _has_incomplete():
        return {'status': 'skipped', 'reason': 'roadmap_has_incomplete'}

    st = _load_state()
    now = int(time.time())
    last = int(st.get('last_seed_ts', 0))
    if now - last < cooldown:
        return {'status': 'skipped', 'reason': 'cooldown_active', 'wait_sec': cooldown - (now - last)}

    seeded = generate_task(write=True)
    st['last_seed_ts'] = now
    _save_state(st)
    return {'status': 'ok', 'seeded': True, 'task_artifact': seeded.get('artifact')}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    p.add_argument('--once', action='store_true')
    p.add_argument('--cooldown', type=int, default=900)
    args = p.parse_args()

    if args.test:
        print(json.dumps({'status': 'ok', 'supports': ['--once', '--cooldown', '--test']}, ensure_ascii=False))
    elif args.once:
        print(json.dumps(run_once(cooldown=args.cooldown), ensure_ascii=False))
    else:
        print(json.dumps({'status': 'idle', 'reason': 'no_action'}, ensure_ascii=False))
