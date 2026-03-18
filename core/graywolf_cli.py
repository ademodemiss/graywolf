#!/usr/bin/env python3
"""Graywolf unified CLI entrypoint.

Commands:
- graywolf status
- graywolf doctor
- graywolf onboard
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path('/home/adem/graywolf')
PY = '/home/adem/.openclaw/workspace/.venv/bin/python'


def _run(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {
        'cmd': ' '.join(cmd),
        'exit_code': p.returncode,
        'stdout': (p.stdout or '').strip(),
        'stderr': (p.stderr or '').strip(),
    }


def cmd_status(args: argparse.Namespace) -> dict:
    r = _run([
        PY, '-m', 'core.runtime', 'status',
        '--session-id', args.session_id,
    ])
    parsed = None
    if r['stdout']:
        try:
            parsed = json.loads(r['stdout'].splitlines()[-1])
        except Exception:
            parsed = {'raw': r['stdout']}

    return {
        'status': 'ok' if r['exit_code'] == 0 else 'error',
        'command': 'status',
        'runtime': parsed,
        'exec': r,
    }


def cmd_doctor(_args: argparse.Namespace) -> dict:
    r = _run(['bash', str(ROOT / 'scripts' / 'release_precheck.sh')])
    return {
        'status': 'ok' if r['exit_code'] == 0 else 'error',
        'command': 'doctor',
        'report_file': str(ROOT / 'reports' / 'release_precheck_latest.md'),
        'exec': r,
    }


def cmd_onboard(_args: argparse.Namespace) -> dict:
    checks = []
    checks.append(_run(['bash', str(ROOT / 'scripts' / 'autonomy_daemon.sh'), 'status']))
    checks.append(_run(['bash', str(ROOT / 'scripts' / 'operator_tasks.sh'), 'all']))

    ok = all(c['exit_code'] == 0 for c in checks)
    return {
        'status': 'ok' if ok else 'error',
        'command': 'onboard',
        'steps': [
            'daemon status check',
            'operator_tasks all smoke',
        ],
        'checks': checks,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='graywolf', description='Graywolf CLI')
    sub = p.add_subparsers(dest='subcommand', required=True)

    sp_status = sub.add_parser('status', help='Show runtime status summary')
    sp_status.add_argument('--session-id', default='graywolf-cli')
    sp_status.set_defaults(handler=cmd_status)

    sp_doctor = sub.add_parser('doctor', help='Run release-grade diagnostics')
    sp_doctor.set_defaults(handler=cmd_doctor)

    sp_onboard = sub.add_parser('onboard', help='Run first-run smoke checks')
    sp_onboard.set_defaults(handler=cmd_onboard)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    out = args.handler(args)
    payload = {'ts': datetime.now().isoformat(), **out}
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if out.get('status') == 'ok' else 1


if __name__ == '__main__':
    raise SystemExit(main())
