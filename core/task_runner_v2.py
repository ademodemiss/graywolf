import argparse
import json
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _run(cmd: str) -> dict:
    p = subprocess.run(shlex.split(cmd), capture_output=True, text=True, check=False)
    return {
        'cmd': cmd,
        'exit_code': p.returncode,
        'stdout': (p.stdout or '').strip(),
        'stderr': (p.stderr or '').strip(),
    }


def run_test(task_path: str) -> dict:
    task = json.loads(Path(task_path).read_text(encoding='utf-8'))
    attempts = []
    for i in range(2):
        results = [_run(c) for c in task.get('verification_commands', [])]
        ok = all(r['exit_code'] == 0 for r in results)
        attempts.append({'attempt': i + 1, 'ok': ok, 'results': results})
        if ok:
            break

    out = {
        'status': 'ok' if attempts[-1]['ok'] else 'failed',
        'task_id': task.get('id'),
        'attempts': attempts,
        'ts': datetime.now(timezone.utc).isoformat(),
    }
    artifact = Path('/home/adem/graywolf/reports/task_runner_v2_report.json')
    artifact.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['artifact'] = str(artifact)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    p.add_argument('--task', default='/home/adem/graywolf/tasks/examples/fix_semantic_search.json')
    a = p.parse_args()
    print(json.dumps(run_test(a.task) if a.test else {'status': 'idle'}, ensure_ascii=False))
