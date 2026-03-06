import argparse
import json
import re
import subprocess
from pathlib import Path

REPORT = Path('/home/adem/graywolf/reports/branch_lifecycle_report.json')


def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {'cmd': ' '.join(cmd), 'exit_code': p.returncode, 'stdout': (p.stdout or '').strip(), 'stderr': (p.stderr or '').strip()}


def _slug(text: str, limit: int = 24) -> str:
    s = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return (s or 'task')[:limit]


def _branch_exists(name: str) -> bool:
    return _run(['git', 'show-ref', '--verify', f'refs/heads/{name}'])['exit_code'] == 0


def pick_branch(task_id: str, title: str) -> dict:
    base = f"task/{task_id}-{_slug(title)}"
    if not _branch_exists(base):
        return {'branch': base, 'collision': False, 'suffix': None}
    i = 2
    while True:
        cand = f"{base}-{i}"
        if not _branch_exists(cand):
            return {'branch': cand, 'collision': True, 'suffix': i}
        i += 1


def run_test() -> dict:
    choice = pick_branch('TASK-001', 'Fix semantic search module import')
    statuses = ['merged', 'closed', 'abandoned']
    out = {
        'status': 'ok',
        'deterministic_branch': choice['branch'],
        'collision_handling': {'collision': choice['collision'], 'suffix': choice['suffix']},
        'lifecycle_model': statuses,
    }
    REPORT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['artifact'] = str(REPORT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
