import argparse
import json
import subprocess
import time


def _run(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    out = (p.stdout or '').strip().splitlines()
    payload = {}
    if out:
        try:
            payload = json.loads(out[-1])
        except Exception:
            payload = {'raw': out[-1]}
    return {'exit_code': p.returncode, 'payload': payload, 'stdout': (p.stdout or '').strip(), 'stderr': (p.stderr or '').strip()}


def run_once(cooldown: int = 900) -> dict:
    loop = _run(['python3', '-m', 'core.agent_loop', '--once'])
    seeded = None
    if loop.get('payload', {}).get('status') == 'idle':
        seeded = _run(['python3', '-m', 'core.idle_seed', '--once', '--cooldown', str(cooldown)])
    return {'status': 'ok', 'agent_loop': loop, 'idle_seed': seeded}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--once', action='store_true')
    p.add_argument('--interval', type=int, default=60)
    p.add_argument('--cooldown', type=int, default=900)
    args = p.parse_args()

    if args.once:
        print(json.dumps(run_once(cooldown=args.cooldown), ensure_ascii=False))
    else:
        while True:
            print(json.dumps(run_once(cooldown=args.cooldown), ensure_ascii=False))
            time.sleep(args.interval)
