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
DAEMON_LOG = ROOT / 'logs' / 'autonomy_daemon.log'
TERMINAL_LOG = ROOT / 'logs' / 'terminal.log'

HELP_MAP = {
    'status': 'graywolf status [--session-id ID] -> runtime/daemon/queue/approval özeti',
    'doctor': 'graywolf doctor -> release precheck gate çalıştırır',
    'onboard': 'graywolf onboard -> daemon + operator smoke checks',
    'approvals': 'graywolf approvals -> pending/granted/denied listesi',
    'commands': 'graywolf commands -> tüm komutları listeler',
    'run': 'graywolf run --intent <intent> [--goal TEXT] [--payload JSON] [--source SRC] [--session-id ID]',
    'approve': 'graywolf approve <request_id> [--actor NAME] -> pending onayı grant eder',
    'deny': 'graywolf deny <request_id> [--actor NAME] -> pending onayı deny eder',
    'logs': 'graywolf logs --target daemon|terminal|precheck [--lines N] -> log gösterir',
    'queue': 'graywolf queue [--limit N] -> queue/processed özet',
    'precheck': 'graywolf precheck -> release precheck gate',
    'monitor': 'graywolf monitor start|stop|status -> daemon kontrol',
    'report': 'graywolf report daily|weekly -> ops summary raporu üretir',
}


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


def cmd_run(args: argparse.Namespace) -> dict:
    payload = {}
    if args.payload:
        try:
            payload = json.loads(args.payload)
        except Exception as e:
            return {'status': 'error', 'command': 'run', 'errors': [f'invalid_payload_json: {e}']}

    if args.goal:
        payload['goal'] = args.goal

    r = _run([
        PY, '-m', 'core.runtime', 'submit-command',
        '--session-id', args.session_id,
        '--intent', args.intent,
        '--payload', json.dumps(payload, ensure_ascii=False),
        '--source', args.source,
    ])

    parsed = None
    if r['stdout']:
        try:
            parsed = json.loads(r['stdout'].splitlines()[-1])
        except Exception:
            parsed = {'raw': r['stdout']}

    status = 'ok' if r['exit_code'] == 0 else 'error'
    return {
        'status': status,
        'command': 'run',
        'intent': args.intent,
        'result': parsed,
        'exec': r,
    }


def cmd_approve(args: argparse.Namespace) -> dict:
    callback_data = f'approval.grant:{args.request_id}'
    r = _run([
        PY, '-m', 'core.runtime', 'approval-callback',
        '--callback-data', callback_data,
        '--actor', args.actor,
    ])
    parsed = None
    if r['stdout']:
        try:
            parsed = json.loads(r['stdout'].splitlines()[-1])
        except Exception:
            parsed = {'raw': r['stdout']}

    return {
        'status': 'ok' if r['exit_code'] == 0 else 'error',
        'command': 'approve',
        'request_id': args.request_id,
        'result': parsed,
        'exec': r,
    }


def cmd_deny(args: argparse.Namespace) -> dict:
    callback_data = f'approval.deny:{args.request_id}'
    r = _run([
        PY, '-m', 'core.runtime', 'approval-callback',
        '--callback-data', callback_data,
        '--actor', args.actor,
    ])
    parsed = None
    if r['stdout']:
        try:
            parsed = json.loads(r['stdout'].splitlines()[-1])
        except Exception:
            parsed = {'raw': r['stdout']}

    return {
        'status': 'ok' if r['exit_code'] == 0 else 'error',
        'command': 'deny',
        'request_id': args.request_id,
        'result': parsed,
        'exec': r,
    }


def cmd_logs(args: argparse.Namespace) -> dict:
    log_map = {
        'daemon': DAEMON_LOG,
        'terminal': TERMINAL_LOG,
        'precheck': ROOT / 'reports' / 'release_precheck_latest.md',
    }
    target = log_map.get(args.target)
    if not target or not target.exists():
        return {'status': 'error', 'command': 'logs', 'errors': [f'log_not_found:{args.target}']}

    lines = target.read_text(encoding='utf-8', errors='replace').splitlines()[-args.lines:]
    return {
        'status': 'ok',
        'command': 'logs',
        'target': args.target,
        'file': str(target),
        'lines': lines,
    }


def cmd_queue(args: argparse.Namespace) -> dict:
    queue_dir = ROOT / 'tasks' / 'queue'
    processed_dir = ROOT / 'tasks' / 'processed'

    q_files = sorted([p.name for p in queue_dir.glob('*.json')]) if queue_dir.exists() else []
    p_files = sorted([p.name for p in processed_dir.glob('*.json')]) if processed_dir.exists() else []

    return {
        'status': 'ok',
        'command': 'queue',
        'summary': {
            'queue_depth': len(q_files),
            'processed_count': len(p_files),
        },
        'last_queued_files': q_files[-args.limit:],
        'last_processed_files': p_files[-args.limit:],
        'dirs': {
            'queue': str(queue_dir),
            'processed': str(processed_dir),
        },
    }


def cmd_precheck(_args: argparse.Namespace) -> dict:
    r = _run(['bash', str(ROOT / 'scripts' / 'release_precheck.sh')])
    return {
        'status': 'ok' if r['exit_code'] == 0 else 'error',
        'command': 'precheck',
        'report_file': str(ROOT / 'reports' / 'release_precheck_latest.md'),
        'exec': r,
    }


def cmd_monitor(args: argparse.Namespace) -> dict:
    action = args.action
    if action == 'start':
        r = _run(['bash', str(ROOT / 'scripts' / 'autonomy_daemon.sh'), 'start'])
    elif action == 'stop':
        r = _run(['bash', str(ROOT / 'scripts' / 'autonomy_daemon.sh'), 'stop'])
    else:
        r = _run(['bash', str(ROOT / 'scripts' / 'autonomy_daemon.sh'), 'status'])

    return {
        'status': 'ok' if r['exit_code'] == 0 else 'error',
        'command': 'monitor',
        'action': action,
        'exec': r,
    }


def cmd_help(args: argparse.Namespace) -> dict:
    topic = (args.topic or '').strip()
    if not topic:
        return {
            'status': 'ok',
            'command': 'help',
            'topics': sorted(HELP_MAP.keys()),
            'hint': 'graywolf help <komut> kullan',
        }

    text = HELP_MAP.get(topic)
    if not text:
        return {
            'status': 'error',
            'command': 'help',
            'errors': [f'unknown_topic:{topic}'],
            'topics': sorted(HELP_MAP.keys()),
        }

    return {
        'status': 'ok',
        'command': 'help',
        'topic': topic,
        'usage': text,
    }


def cmd_report(args: argparse.Namespace) -> dict:
    kind = args.kind

    status_run = _run([PY, '-m', 'core.runtime', 'status', '--session-id', 'graywolf-report'])
    queue_run = _run([str(ROOT / 'scripts' / 'graywolf'), 'queue', '--limit', '5'])

    status_json = None
    queue_json = None
    if status_run['stdout']:
        try:
            status_json = json.loads(status_run['stdout'].splitlines()[-1])
        except Exception:
            status_json = {'raw': status_run['stdout']}
    if queue_run['stdout']:
        try:
            queue_json = json.loads(queue_run['stdout'].splitlines()[-1])
        except Exception:
            queue_json = {'raw': queue_run['stdout']}

    report_file = ROOT / 'reports' / f'{kind}_ops_summary_latest.md'
    report_file.parent.mkdir(parents=True, exist_ok=True)

    runtime = status_json if isinstance(status_json, dict) else {}
    approval = runtime.get('approval', {}) if isinstance(runtime, dict) else {}
    queue = runtime.get('queue', {}) if isinstance(runtime, dict) else {}

    lines = [
        f'# Graywolf {kind.capitalize()} Ops Summary',
        '',
        f'- generated_at: {datetime.now().isoformat()}',
        f"- daemon_status: {((runtime.get('daemon') or {}).get('status') if isinstance(runtime, dict) else 'unknown')}",
        f"- queue_depth: {queue.get('queue_depth', 'n/a')}",
        f"- processed_count: {queue.get('processed_count', 'n/a')}",
        f"- pending_command_approvals: {approval.get('pending_command_approvals', 'n/a')}",
        '',
        '## Last processed tasks',
    ]

    for item in (queue.get('last_5_processed') or []):
        lines.append(f"- {item.get('task_id')} | intent={item.get('intent')} | status={item.get('status')} | source={item.get('source')}")

    if not (queue.get('last_5_processed') or []):
        lines.append('- none')

    lines += [
        '',
        '## Command outputs',
        f"- runtime status exit: {status_run.get('exit_code')}",
        f"- queue summary exit: {queue_run.get('exit_code')}",
        '',
    ]

    report_file.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    return {
        'status': 'ok' if status_run['exit_code'] == 0 else 'error',
        'command': 'report',
        'kind': kind,
        'report_file': str(report_file),
        'runtime_status': status_json,
        'queue_status': queue_json,
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

    sp_run = sub.add_parser('run', help='Submit an intent command quickly')
    sp_run.add_argument('--intent', required=True)
    sp_run.add_argument('--goal', default='')
    sp_run.add_argument('--payload', default='{}', help='JSON payload')
    sp_run.add_argument('--source', default='graywolf-cli')
    sp_run.add_argument('--session-id', default='graywolf-cli')
    sp_run.set_defaults(handler=cmd_run)

    sp_approve = sub.add_parser('approve', help='Approve a pending request id')
    sp_approve.add_argument('request_id')
    sp_approve.add_argument('--actor', default='graywolf-cli')
    sp_approve.set_defaults(handler=cmd_approve)

    sp_deny = sub.add_parser('deny', help='Deny a pending request id')
    sp_deny.add_argument('request_id')
    sp_deny.add_argument('--actor', default='graywolf-cli')
    sp_deny.set_defaults(handler=cmd_deny)

    sp_logs = sub.add_parser('logs', help='Read key logs quickly')
    sp_logs.add_argument('--target', choices=['daemon', 'terminal', 'precheck'], default='daemon')
    sp_logs.add_argument('--lines', type=int, default=30)
    sp_logs.set_defaults(handler=cmd_logs)

    sp_queue = sub.add_parser('queue', help='Show queue/processed summary')
    sp_queue.add_argument('--limit', type=int, default=10)
    sp_queue.set_defaults(handler=cmd_queue)

    sp_precheck = sub.add_parser('precheck', help='Run release precheck gate')
    sp_precheck.set_defaults(handler=cmd_precheck)

    sp_monitor = sub.add_parser('monitor', help='Monitor daemon controls')
    sp_monitor.add_argument('action', choices=['start', 'stop', 'status'])
    sp_monitor.set_defaults(handler=cmd_monitor)

    sp_report = sub.add_parser('report', help='Generate ops summary report')
    sp_report.add_argument('kind', choices=['daily', 'weekly'])
    sp_report.set_defaults(handler=cmd_report)

    sp_help = sub.add_parser('help', help='Show usage for a specific command')
    sp_help.add_argument('topic', nargs='?', default='')
    sp_help.set_defaults(handler=cmd_help)

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
