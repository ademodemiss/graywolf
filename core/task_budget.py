import argparse
import json
import shlex
import subprocess
import time
from pathlib import Path

REPORT = Path('/home/adem/graywolf/reports/task_budget_report.json')


def _run_with_timeout(cmd: str, timeout_sec: float) -> dict:
    start = time.time()
    try:
        p = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=timeout_sec, check=False)
        dur = int((time.time() - start) * 1000)
        return {
            'cmd': cmd,
            'exit_code': p.returncode,
            'timeout': False,
            'duration_ms': dur,
            'stdout': (p.stdout or '').strip(),
            'stderr': (p.stderr or '').strip(),
        }
    except subprocess.TimeoutExpired:
        dur = int((time.time() - start) * 1000)
        return {
            'cmd': cmd,
            'exit_code': -9,
            'timeout': True,
            'duration_ms': dur,
            'stdout': '',
            'stderr': 'timeout',
        }


def run_test() -> dict:
    # deterministic timeout scenario
    quick = _run_with_timeout("python3 -c \"print('ok')\"", timeout_sec=2)
    slow = _run_with_timeout("python3 -c \"import time; time.sleep(2); print('done')\"", timeout_sec=0.3)

    max_attempts = 1
    attempts = 1
    budget_exceeded = slow['timeout']

    out = {
        'status': 'ok' if quick['exit_code'] == 0 and budget_exceeded else 'failed',
        'duration': {
            'quick_ms': quick['duration_ms'],
            'slow_ms': slow['duration_ms'],
        },
        'attempt': attempts,
        'timeout': slow['timeout'],
        'budget_exceeded': budget_exceeded,
        'runs': {'quick': quick, 'slow': slow},
        'policy': {'max_attempts': max_attempts, 'timeout_sec': 0.3},
    }
    REPORT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['artifact'] = str(REPORT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
