import argparse
import json
import shlex
import subprocess
from concurrent.futures import ThreadPoolExecutor


def _run(cmd: str) -> dict:
    p = subprocess.run(shlex.split(cmd), capture_output=True, text=True, check=False)
    return {'cmd': cmd, 'exit_code': p.returncode, 'stdout': (p.stdout or '').strip(), 'stderr': (p.stderr or '').strip()}


def run_parallel(commands: list[str], max_workers: int = 4) -> dict:
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        results = list(ex.map(_run, commands))
    ok = all(r['exit_code'] == 0 for r in results)
    return {'status': 'ok' if ok else 'failed', 'results': results}


def run_test() -> dict:
    cmds = [
        "python3 -c \"print('p1')\"",
        "python3 -c \"print('p2')\"",
    ]
    out = run_parallel(cmds, max_workers=2)
    return {'status': out['status'], 'count': len(out['results']), 'all_zero': all(r['exit_code'] == 0 for r in out['results'])}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    if args.test:
        print(json.dumps(run_test(), ensure_ascii=False))
    else:
        print(json.dumps({'status': 'idle'}, ensure_ascii=False))
