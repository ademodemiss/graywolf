import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

IDLE_DIR = Path('/home/adem/graywolf/memory/idle_tasks')


def _build_task() -> dict:
    ts = datetime.now(timezone.utc).isoformat()
    return {
        'id': f'IDLE-{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")}',
        'title': 'Idle Seeded Maintenance Task',
        'goal': 'Run lightweight maintenance checks during idle windows',
        'context': 'agent_loop returned idle/no_incomplete_milestone',
        'constraints': ['safe commands only', 'no destructive actions'],
        'acceptance_criteria': ['verification commands exit_code=0'],
        'evidence_requirements': ['terminal.log entry', 'state snapshot'],
        'created_at': ts,
    }


def generate_task(write: bool = False) -> dict:
    task = _build_task()
    out = {'status': 'ok', 'task': task}
    if write:
        IDLE_DIR.mkdir(parents=True, exist_ok=True)
        fname = IDLE_DIR / f"idle_task_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        fname.write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding='utf-8')
        out['artifact'] = str(fname)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    if args.test or args.write:
        print(json.dumps(generate_task(write=args.write), ensure_ascii=False))
    else:
        print(json.dumps({'status': 'idle', 'reason': 'no_action'}, ensure_ascii=False))
