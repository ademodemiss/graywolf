import argparse
import json
import subprocess
from pathlib import Path

TASKS = [
    '/home/adem/graywolf/tasks/examples/fix_semantic_search.json'
]


def _run(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {'cmd': ' '.join(cmd), 'exit_code': p.returncode, 'stdout': (p.stdout or '').strip(), 'stderr': (p.stderr or '').strip()}


def run_test() -> dict:
    results = []
    ok = True
    for task in TASKS:
        r = _run(['python3', '-m', 'core.task_runner_v2', '--test', '--task', task])
        results.append(r)
        if r['exit_code'] != 0:
            ok = False
    out = {'status': 'ok' if ok else 'failed', 'tasks': TASKS, 'results': results}
    Path('/home/adem/graywolf/reports/task_queue_runner_report.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
