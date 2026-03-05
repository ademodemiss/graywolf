import argparse
import json
import subprocess


def _run(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {
        'cmd': ' '.join(cmd),
        'exit_code': p.returncode,
        'stdout': (p.stdout or '').strip(),
        'stderr': (p.stderr or '').strip(),
    }


def run_test() -> dict:
    active = _run(['systemctl', 'is-active', 'graywolf'])
    journal = _run(['journalctl', '-u', 'graywolf', '-n', '10', '--no-pager'])

    status = 'ok'
    if active['exit_code'] != 0:
        status = 'warn'
    if journal['exit_code'] != 0:
        status = 'warn'

    return {
        'status': status,
        'service': {
            'is_active': active['stdout'] if active['stdout'] else 'unknown',
            'probe': active,
        },
        'journal_tail': journal,
    }


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    out = run_test() if args.test else {'status': 'idle'}
    print(json.dumps(out, ensure_ascii=False))
