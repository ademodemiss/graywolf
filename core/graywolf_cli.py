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
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path('/home/adem/graywolf')
PY = '/home/adem/.openclaw/workspace/.venv/bin/python'
PENDING_APPROVALS_FILE = ROOT / 'sessions' / 'pending_approvals.json'
CLI_COMMANDS_FILE = ROOT / 'docs' / 'CLI_COMMANDS.md'


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


def cmd_approvals(_args: argparse.Namespace) -> dict:
    if not PENDING_APPROVALS_FILE.exists():
        return {
            'status': 'ok',
            'command': 'approvals',
            'summary': {'pending': 0, 'granted': 0, 'denied': 0, 'skipped': 0, 'total': 0},
            'latest': [],
        }

    try:
        data = json.loads(PENDING_APPROVALS_FILE.read_text(encoding='utf-8'))
    except Exception as e:
        return {'status': 'error', 'command': 'approvals', 'errors': [str(e)]}

    items = list(data.items())
    counts = Counter((v or {}).get('status', 'unknown') for _k, v in items)
    latest = []
    for rid, item in sorted(items, key=lambda kv: (kv[1] or {}).get('created_at', ''))[-10:]:
        latest.append({
            'request_id': rid,
            'status': (item or {}).get('status'),
            'intent': ((item or {}).get('envelope') or {}).get('intent'),
            'source': ((item or {}).get('envelope') or {}).get('source'),
            'created_at': (item or {}).get('created_at'),
            'resolved_at': (item or {}).get('resolved_at'),
        })

    return {
        'status': 'ok',
        'command': 'approvals',
        'summary': {
            'pending': counts.get('pending', 0),
            'granted': counts.get('granted', 0),
            'denied': counts.get('denied', 0),
            'skipped': counts.get('skipped', 0),
            'total': len(items),
        },
        'latest': latest,
        'file': str(PENDING_APPROVALS_FILE),
    }


def cmd_commands(_args: argparse.Namespace) -> dict:
    text = ''
    if CLI_COMMANDS_FILE.exists():
        text = CLI_COMMANDS_FILE.read_text(encoding='utf-8')
    return {
        'status': 'ok',
        'command': 'commands',
        'commands_file': str(CLI_COMMANDS_FILE),
        'content': text,
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

    sp_approvals = sub.add_parser('approvals', help='Show approval queue summary')
    sp_approvals.set_defaults(handler=cmd_approvals)

    sp_commands = sub.add_parser('commands', help='Show available Graywolf CLI commands')
    sp_commands.set_defaults(handler=cmd_commands)

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
