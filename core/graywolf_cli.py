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
import os
import subprocess
import sys
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from agent.command_parser import parse_command
from agent.simple_agent_loop import (
    build_plan,
    find_state_by_request_id,
    load_agent_state,
    run_agent_loop,
    save_agent_state,
    wait_for_task_completion,
)
from core.assistant_context import assemble_assistant_context
from core.assistant_explainer import explain_execution, score_ux_output

ROOT = Path('/home/adem/graywolf')
PY = '/home/adem/.openclaw/workspace/.venv/bin/python'
PENDING_APPROVALS_FILE = ROOT / 'sessions' / 'pending_approvals.json'
CLI_COMMANDS_FILE = ROOT / 'docs' / 'CLI_COMMANDS.md'
DAEMON_LOG = ROOT / 'logs' / 'autonomy_daemon.log'
TERMINAL_LOG = ROOT / 'logs' / 'terminal.log'
AGENT_RUNS_DIR = ROOT / 'sessions' / 'agent_runs'

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
    'agent': 'graywolf agent --goal "..." [--max-steps 5] [--plan-only] -> tek ajan planla/yürüt',
    'assistant': 'graywolf assistant --message "..." [--max-steps 5] -> doğal dilden goal çıkarıp agent çalıştır',
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

    status = 'ok' if r['exit_code'] == 0 else 'error'
    queue = (parsed or {}).get('queue', {}) if isinstance(parsed, dict) else {}
    daemon = (parsed or {}).get('daemon', {}) if isinstance(parsed, dict) else {}

    ux = {
        'summary': f"Daemon: {daemon.get('status', 'unknown')}, queue_depth: {queue.get('queue_depth', 'n/a')}",
        'next_step': 'Detay için `graywolf logs --target daemon --lines 30` çalıştırabilirsin.' if status == 'ok' else '`graywolf precheck` ile hızlı teşhis yap.',
    }

    return {
        'status': status,
        'command': 'status',
        'runtime': parsed,
        'ux': ux,
        'ux_quality': score_ux_output(ux),
        'exec': r,
    }


def cmd_doctor(_args: argparse.Namespace) -> dict:
    r = _run(['bash', str(ROOT / 'scripts' / 'release_precheck.sh')])
    status = 'ok' if r['exit_code'] == 0 else 'error'
    ux = {
        'summary': 'Release precheck başarılı.' if status == 'ok' else 'Release precheck hata verdi.',
        'next_step': 'Raporu `graywolf logs --target precheck --lines 80` ile inceleyebilirsin.' if status == 'ok' else '`graywolf logs --target precheck --lines 120` ile hata detayını incele.',
    }
    return {
        'status': status,
        'command': 'doctor',
        'report_file': str(ROOT / 'reports' / 'release_precheck_latest.md'),
        'ux': ux,
        'ux_quality': score_ux_output(ux),
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
        summary = {'pending': 0, 'granted': 0, 'denied': 0, 'skipped': 0, 'total': 0}
        return {
            'status': 'ok',
            'command': 'approvals',
            'summary': summary,
            'latest': [],
            'ux': {
                'summary': 'Bekleyen onay yok.',
                'next_step': 'Yeni onay çıktığında `graywolf approvals` ile kontrol edebilirsin.',
            },
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

    summary = {
        'pending': counts.get('pending', 0),
        'granted': counts.get('granted', 0),
        'denied': counts.get('denied', 0),
        'skipped': counts.get('skipped', 0),
        'total': len(items),
    }

    return {
        'status': 'ok',
        'command': 'approvals',
        'summary': summary,
        'latest': latest,
        'file': str(PENDING_APPROVALS_FILE),
        'ux': {
            'summary': f"Bekleyen onay: {summary['pending']}, grant: {summary['granted']}, deny: {summary['denied']}",
            'next_step': 'Bekleyen varsa `graywolf approve <request_id>` veya `graywolf deny <request_id>` kullan.',
        },
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

    execution_status = ((parsed or {}).get('status') if isinstance(parsed, dict) else None) or ('error' if status == 'error' else 'queued')
    task_id = ((parsed or {}).get('task') or {}).get('task_id') if isinstance(parsed, dict) else None
    ux = explain_execution({
        'status': execution_status,
        'intent': args.intent,
        'task_id': task_id,
    })

    return {
        'status': status,
        'command': 'run',
        'intent': args.intent,
        'result': parsed,
        'ux': ux,
        'ux_quality': score_ux_output(ux),
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

    status = 'ok' if r['exit_code'] == 0 else 'error'
    exec_status = 'queued' if status == 'ok' else 'error'
    task_id = (((parsed or {}).get('queued') or {}).get('task') or {}).get('task_id') if isinstance(parsed, dict) else None
    ux = explain_execution({
        'status': exec_status,
        'intent': 'approve',
        'task_id': task_id,
        'errors': (parsed or {}).get('errors') if isinstance(parsed, dict) else None,
    })

    out = {
        'status': status,
        'command': 'approve',
        'request_id': args.request_id,
        'result': parsed,
        'ux': ux,
        'exec': r,
    }

    if status != 'ok':
        return out

    state = find_state_by_request_id(str(AGENT_RUNS_DIR), args.request_id)
    if not state:
        return out

    out['run_id'] = state.get('run_id')

    continuity = dict((state or {}).get('continuity') or {})
    approved_ids = list(continuity.get('approved_request_ids') or [])
    if args.request_id not in approved_ids:
        approved_ids.append(args.request_id)
    continuity['approved_request_ids'] = approved_ids
    continuity['approve_count'] = len(approved_ids)
    state['continuity'] = continuity

    pause = (state or {}).get('pause') or {}
    pause_step = int(pause.get('step_index') or 1)

    tracked = None
    if task_id:
        tracked = wait_for_task_completion(task_id, processed_dir=str(ROOT / 'tasks' / 'processed'), timeout_seconds=360)

    trace = list((state or {}).get('trace') or [])
    plan = list((state or {}).get('plan') or [])
    if tracked and plan and 1 <= pause_step <= len(plan):
        trace.append({
            'index': pause_step,
            'step': plan[pause_step - 1],
            'attempts': 1,
            'result': {'status': tracked.get('status'), 'summary': tracked.get('summary')},
            'summary': tracked.get('summary', ''),
            'evaluation': {'accepted': tracked.get('status') == 'completed', 'status': tracked.get('status'), 'reason': 'resume_gate'},
        })

    if tracked and tracked.get('status') != 'completed':
        state['status'] = 'error'
        state['trace'] = trace
        state['final'] = {
            'state': 'yarım kaldı',
            'reason': tracked.get('summary', 'Onay sonrası adım tamamlanamadı.'),
        }
        save_agent_state(str(AGENT_RUNS_DIR), state['run_id'], state)
        out['agent_resume'] = {
            'status': 'error',
            'run_id': state.get('run_id'),
            'final': state['final'],
        }
        return out

    state['trace'] = trace
    state['status'] = 'resuming'
    state['next_step_index'] = pause_step + 1
    save_agent_state(str(AGENT_RUNS_DIR), state['run_id'], state)

    resume_cmd = [
        str(ROOT / 'scripts' / 'graywolf'), 'agent',
        '--goal', state.get('goal', ''),
        '--session-id', state.get('session_id', 'graywolf-agent'),
        '--source', state.get('source', 'graywolf-agent'),
        '--max-steps', str(state.get('max_steps', 4)),
        '--resume-run-id', state.get('run_id', ''),
    ]
    rr = _run(resume_cmd)
    resumed = None
    if rr.get('stdout'):
        try:
            resumed = json.loads(rr['stdout'].splitlines()[-1])
        except Exception:
            resumed = {'raw': rr['stdout']}

    out['agent_resume'] = resumed or {'status': 'error', 'errors': ['resume_parse_failed']}
    return out


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

    status = 'ok' if r['exit_code'] == 0 else 'error'
    ux = {
        'summary': 'Onay isteği reddedildi.' if status == 'ok' else 'Onay reddetme sırasında hata oluştu.',
        'next_step': 'Durumu `graywolf approvals` ile kontrol edebilirsin.' if status == 'ok' else '`graywolf logs --target daemon --lines 50` ile hatayı incele.',
    }

    return {
        'status': status,
        'command': 'deny',
        'request_id': args.request_id,
        'result': parsed,
        'ux': ux,
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
    summary = {
        'queue_depth': len(q_files),
        'processed_count': len(p_files),
    }

    return {
        'status': 'ok',
        'command': 'queue',
        'summary': summary,
        'last_queued_files': q_files[-args.limit:],
        'last_processed_files': p_files[-args.limit:],
        'dirs': {
            'queue': str(queue_dir),
            'processed': str(processed_dir),
        },
        'ux': {
            'summary': f"Kuyrukta {summary['queue_depth']} iş var, toplam işlenen {summary['processed_count']}.",
            'next_step': 'Bekleme artarsa `graywolf monitor status` ve `graywolf logs --target daemon --lines 50` ile kontrol et.',
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

    status = 'ok' if r['exit_code'] == 0 else 'error'
    summary = f"Monitor action `{action}` {'başarılı' if status == 'ok' else 'hatalı'} tamamlandı."
    next_step = 'Servis durumunu doğrulamak için `graywolf monitor status` çalıştır.' if status == 'ok' else '`graywolf logs --target daemon --lines 50` ile hatayı incele.'

    return {
        'status': status,
        'command': 'monitor',
        'action': action,
        'ux': {
            'summary': summary,
            'next_step': next_step,
        },
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
            'ux': {
                'summary': 'Komut yardımı listelendi.',
                'next_step': 'Detay görmek için `graywolf help <komut>` çalıştır.',
            },
        }

    text = HELP_MAP.get(topic)
    if not text:
        return {
            'status': 'error',
            'command': 'help',
            'errors': [f'unknown_topic:{topic}'],
            'topics': sorted(HELP_MAP.keys()),
            'ux': {
                'summary': f'Bilinmeyen help konusu: {topic}',
                'next_step': 'Geçerli başlıklar için `graywolf help` çalıştır.',
            },
        }

    return {
        'status': 'ok',
        'command': 'help',
        'topic': topic,
        'usage': text,
        'ux': {
            'summary': f'`{topic}` komutu için kullanım gösterildi.',
            'next_step': f'Komutu çalıştırmak için: {text}',
        },
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

    status = 'ok' if status_run['exit_code'] == 0 else 'error'
    return {
        'status': status,
        'command': 'report',
        'kind': kind,
        'report_file': str(report_file),
        'runtime_status': status_json,
        'queue_status': queue_json,
        'ux': {
            'summary': f'{kind} ops raporu üretildi: {report_file.name}' if status == 'ok' else f'{kind} ops raporu üretimi başarısız.',
            'next_step': f'Raporu aç: {report_file}' if status == 'ok' else '`graywolf status` ve `graywolf logs --target daemon --lines 50` ile teşhis et.',
        },
    }


VALID_ASSISTANT_INTENTS = {'deploy', 'healthcheck', 'analyze', 'execute', 'chat_command'}


ASSISTANT_TOOL_ROUTE = {
    'deploy': {'route': 'approval_required', 'tool_family': 'runtime.submit_command', 'risk': 'high'},
    'healthcheck': {'route': 'direct_safe', 'tool_family': 'runtime.status_or_health', 'risk': 'low'},
    'analyze': {'route': 'analysis_first', 'tool_family': 'orchestrator.analysis', 'risk': 'medium'},
    'execute': {'route': 'confirm_first', 'tool_family': 'runtime.submit_command', 'risk': 'medium'},
    'chat_command': {'route': 'safe_execute', 'tool_family': 'runtime.submit_command', 'risk': 'low'},
}


def _extract_json_dict(raw: str) -> dict | None:
    text = (raw or '').strip()
    if not text:
        return None
    if text.startswith('```'):
        lines = [ln for ln in text.splitlines() if not ln.strip().startswith('```')]
        text = '\n'.join(lines).strip()
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _normalize_intent(intent: str | None, default_intent: str) -> str:
    candidate = str(intent or '').strip().lower()
    if candidate in VALID_ASSISTANT_INTENTS:
        return candidate
    return default_intent


def _orchestration_hint(intent: str | None) -> dict:
    normalized = _normalize_intent(intent, 'execute')
    hint = ASSISTANT_TOOL_ROUTE.get(normalized, ASSISTANT_TOOL_ROUTE['execute']).copy()
    hint['intent'] = normalized
    return hint


def _assistant_output_contract(*, mode: str, triage: dict, ux: dict, orchestration_hint: dict | None = None) -> dict:
    return {
        'contract_version': 'v1',
        'mode': mode,
        'triage': {
            'kind': (triage or {}).get('kind'),
            'reason': (triage or {}).get('reason'),
        },
        'response': {
            'summary': (ux or {}).get('summary', ''),
            'next_step': (ux or {}).get('next_step', ''),
        },
        'orchestration': orchestration_hint or {},
    }


def _infer_goal_with_llm(message: str, context_blob: str = '') -> dict:
    text = (message or '').strip()
    if not text:
        return {'goal': '', 'intent': 'execute', 'confidence': 0.0, 'provider': 'none'}

    parsed = parse_command(text, source='graywolf-assistant')
    inferred = {
        'goal': text,
        'intent': parsed.get('intent', 'execute'),
        'confidence': float(parsed.get('confidence', 0.2)),
        'provider': 'heuristic',
    }

    if os.getenv('GW_ASSISTANT_LLM', '1').strip().lower() in {'0', 'false', 'off', 'no'}:
        return inferred

    try:
        from core.llm_router import LLMRouter

        llm = LLMRouter().get()
        prompt = (
            'Aşağıdaki kullanıcı mesajından kısa bir uygulanabilir goal çıkar. '
            'Sadece JSON döndür: {"goal": "...", "intent": "deploy|healthcheck|analyze|execute|chat_command", "confidence": 0.0}.\n\n'
            f'Mesaj: {text}\n\n'
            f'Bağlam özeti:\n{context_blob}'
        )
        raw = llm.generate_response(prompt)
        if isinstance(raw, str):
            data = _extract_json_dict(raw)
            if isinstance(data, dict):
                llm_goal = str(data.get('goal', '')).strip()
                llm_intent = _normalize_intent(data.get('intent'), inferred['intent'])
                try:
                    llm_confidence = float(data.get('confidence', 0.0))
                except Exception:
                    llm_confidence = 0.0

                # Conservative adoption: intent/goal only if usable.
                if llm_goal:
                    inferred['goal'] = llm_goal
                inferred['intent'] = llm_intent
                if llm_goal or llm_intent != parsed.get('intent', 'execute'):
                    inferred['provider'] = 'llm'
                    inferred['confidence'] = max(inferred['confidence'], min(max(llm_confidence, 0.0), 1.0), 0.7)
    except Exception:
        pass

    return inferred


def _infer_triage_with_llm(message: str, context_blob: str = '') -> dict | None:
    text = (message or '').strip()
    if not text:
        return None

    # Kolay rollback: GW_TRIAGE_LLM=0 ile LLM triage tamamen kapanır.
    if os.getenv('GW_TRIAGE_LLM', '1').strip().lower() in {'0', 'false', 'off', 'no'}:
        return None

    try:
        from core.llm_router import LLMRouter

        llm = LLMRouter().get()
        prompt = (
            'Kullanıcı mesajını sınıflandır. Sadece JSON döndür. Ek metin yazma.\\n'
            '{"kind":"chat|task|unclear", "confidence":0.0, "reason":"short", '
            '"intent":"deploy|healthcheck|analyze|execute|chat_command|null", '
            '"goal":"short or empty"}\\n\\n'
            f'Mesaj: {text}\\n\\n'
            f'Bağlam özeti:\\n{context_blob}'
        )
        raw = llm.generate_response(prompt)
        if not isinstance(raw, str):
            return None

        data = _extract_json_dict(raw)
        if not isinstance(data, dict):
            return None

        kind = str(data.get('kind', '')).strip().lower()
        if kind not in {'chat', 'task', 'unclear'}:
            return None

        try:
            confidence = float(data.get('confidence', 0.0))
        except Exception:
            confidence = 0.0

        reason = str(data.get('reason') or '').strip()[:64] or f'llm_{kind}'
        return {
            'kind': kind,
            'confidence': min(max(confidence, 0.0), 1.0),
            'reason': reason,
            'intent': _normalize_intent(data.get('intent'), 'execute') if data.get('intent') is not None else None,
            'goal': data.get('goal'),
        }
    except Exception:
        return None


def _normalize_for_match(text: str) -> str:
    base = (text or '').strip().casefold()
    decomposed = unicodedata.normalize('NFKD', base)
    cleaned = ''.join(ch for ch in decomposed if not unicodedata.combining(ch))
    tr_map = str.maketrans({
        'ı': 'i',
        'ğ': 'g',
        'ş': 's',
        'ö': 'o',
        'ü': 'u',
        'ç': 'c',
    })
    return cleaned.translate(tr_map)


def _triage_message_kind(message: str, context_blob: str = '') -> tuple[str, str]:
    text = _normalize_for_match(message)
    triage_debug = os.getenv('GW_TRIAGE_DEBUG', '0').strip().lower() in {'1', 'true', 'on', 'yes'}
    if not text:
        if triage_debug:
            print('ASSISTANT_TRIAGE rule=empty final=chat reason=empty')
        return 'chat', 'empty'

    chat_patterns = (
        'merhaba', 'selam', 'nasilsin', 'iyi misin',
        'bana ne yapabildigini soyle', 'yardim', 'help',
        'sen kimsin', 'kimsin',
        'hava durumu', 'hava nasil', 'sicaklik',
    )
    task_patterns = (
        ' yaz', 'olustur', 'yap', 'calistir', 'duzelt', 'analiz et', 'rapor hazirla', 'script olustur',
    )
    question_patterns = ('?', ' nedir', ' ne ', ' nasil', ' kim ', ' kimdir', ' kac', 'hangi ')

    if any(p in text for p in chat_patterns):
        if triage_debug:
            print('ASSISTANT_TRIAGE rule=chat_pattern final=chat reason=chat_pattern')
        return 'chat', 'chat_pattern'

    if any(p in text for p in task_patterns):
        if triage_debug:
            print('ASSISTANT_TRIAGE rule=task_pattern final=task reason=task_pattern')
        return 'task', 'task_pattern'

    if any(p in text for p in question_patterns):
        if triage_debug:
            print('ASSISTANT_TRIAGE rule=chat_question final=chat reason=chat_question')
        return 'chat', 'chat_question'

    llm_triage = _infer_triage_with_llm(message, context_blob=context_blob)
    if not llm_triage:
        if triage_debug:
            print('ASSISTANT_TRIAGE llm=none final=chat reason=uncertain_clarify')
        return 'chat', 'uncertain_clarify'

    llm_kind = str(llm_triage.get('kind') or '').strip().lower()
    try:
        llm_confidence = float(llm_triage.get('confidence') or 0.0)
    except Exception:
        llm_confidence = 0.0

    if llm_kind == 'task' and llm_confidence >= 0.70:
        if triage_debug:
            print(f'ASSISTANT_TRIAGE llm={llm_kind}:{llm_confidence:.2f} final=task reason=llm_task')
        return 'task', 'llm_task'

    if llm_kind == 'chat' and llm_confidence >= 0.55:
        if triage_debug:
            print(f'ASSISTANT_TRIAGE llm={llm_kind}:{llm_confidence:.2f} final=chat reason=llm_chat')
        return 'chat', 'llm_chat'

    if llm_kind == 'unclear':
        if triage_debug:
            print(f'ASSISTANT_TRIAGE llm={llm_kind}:{llm_confidence:.2f} final=unclear reason=llm_unclear')
        return 'unclear', 'llm_unclear'

    if triage_debug:
        print(f'ASSISTANT_TRIAGE llm={llm_kind}:{llm_confidence:.2f} final=chat reason=uncertain_clarify')
    return 'chat', 'uncertain_clarify'


def cmd_assistant(args: argparse.Namespace) -> dict:
    message = (args.message or '').strip()
    if not message:
        return {'status': 'error', 'command': 'assistant', 'errors': ['empty_message']}

    context_pack = assemble_assistant_context(message=message, session_id=args.session_id, source=args.source)
    context_blob = context_pack.get('context_blob', '')

    kind, triage_reason = _triage_message_kind(message, context_blob=context_blob)
    normalized_message = _normalize_for_match(message)
    if kind in {'chat', 'unclear'}:
        if triage_reason in {'uncertain_clarify', 'llm_unclear'} or kind == 'unclear':
            summary = 'Mesajı görev mi sohbet mi net ayıramadım.'
            next_step = 'Kısa net görev yaz: örn. `iki sayıyı toplayan script yaz`.'
        elif triage_reason == 'chat_question':
            summary = 'Sorunu sohbet sorusu olarak algıladım.'
            next_step = 'Detay istersen daha net sor: örn. `Giresun bugün hava durumu` veya `Python list nedir?`.'
        elif 'yardim' in normalized_message or 'help' in normalized_message or 'ne yapabildigini' in normalized_message:
            summary = 'Graywolf: görev planlama/yürütme, approval-resume, precheck ve kısa operasyon raporları yapabilirim.'
            next_step = 'Görev vermek için: `bir python script yaz` gibi net bir istek yaz.'
        elif 'sen kimsin' in normalized_message or 'kimsin' in normalized_message:
            summary = 'Ben Graywolf asistanıyım; sohbet ederim ve verdiğin görevleri güvenli akışla planlayıp yürütürüm.'
            next_step = 'İstersen hemen bir görev ver: `iki sayıyı toplayan script yaz`.'
        elif 'hava durumu' in normalized_message or 'hava nasil' in normalized_message or 'sicaklik' in normalized_message:
            summary = 'Hava durumu sorusu sohbet olarak algılandı.'
            next_step = 'Canlı veri için şehir + zaman belirt: örn. `Giresun bugün hava durumu`.'
        else:
            summary = 'Merhaba 👋 Buradayım. Sohbet edebiliriz veya görev verebilirsin.'
            next_step = 'Görev için örnek: `iki sayıyı toplayan script yaz`.'

        ux = {'summary': summary, 'next_step': next_step}
        triage = {'kind': kind, 'reason': triage_reason}
        return {
            'status': 'ok',
            'command': 'assistant',
            'mode': 'chat',
            'message': message,
            'triage': triage,
            'assistant_output': _assistant_output_contract(mode='chat', triage=triage, ux=ux),
            'context_budget': {
                'max_tokens': context_pack.get('max_tokens'),
                'used_tokens': context_pack.get('used_tokens'),
                'sections': context_pack.get('sections'),
            },
            'ux': ux,
            'ux_quality': score_ux_output(ux),
        }

    inferred = _infer_goal_with_llm(message, context_blob=context_blob)
    goal = (inferred.get('goal') or '').strip()
    if not goal:
        return {'status': 'error', 'command': 'assistant', 'errors': ['empty_goal_after_parse']}

    plan = build_plan(goal, max_steps=args.max_steps)

    if args.plan_only:
        ux = {
            'summary': f'Goal çıkarıldı ve plan hazır ({len(plan)} adım).',
            'next_step': 'Yürütmek için `graywolf assistant --message "..."` komutunu plan-only olmadan çalıştır.',
        }
        orchestration_hint = _orchestration_hint(inferred.get('intent'))
        triage = {'kind': kind, 'reason': triage_reason}
        return {
            'status': 'ok',
            'command': 'assistant',
            'mode': 'plan_only',
            'message': message,
            'goal': goal,
            'intent': inferred.get('intent'),
            'inference': inferred,
            'orchestration_hint': orchestration_hint,
            'triage': triage,
            'assistant_output': _assistant_output_contract(mode='plan_only', triage=triage, ux=ux, orchestration_hint=orchestration_hint),
            'context_budget': {
                'max_tokens': context_pack.get('max_tokens'),
                'used_tokens': context_pack.get('used_tokens'),
                'sections': context_pack.get('sections'),
            },
            'plan': plan,
            'ux': ux,
            'ux_quality': score_ux_output(ux),
        }

    agent_args = SimpleNamespace(
        goal=goal,
        max_steps=args.max_steps,
        source=args.source,
        session_id=args.session_id,
        plan_only=False,
        resume_run_id='',
    )
    agent_out = cmd_agent(agent_args)

    trace = list(agent_out.get('trace') or [])
    progress = {
        'planned_steps': len(agent_out.get('plan') or plan),
        'completed_steps': int(agent_out.get('completed_steps') or 0),
        'trace_steps': len(trace),
    }
    final = agent_out.get('final') or {}

    ux = {
        'summary': f"Goal işlendi: {goal[:120]}. Son durum: {final.get('classification', agent_out.get('status', 'unknown'))}.",
        'next_step': 'Onay gerekiyorsa `graywolf approvals` + `graywolf approve <request_id>` ile devam et.' if agent_out.get('status') == 'confirm_required' else 'Detay için trace/final alanlarını inceleyebilirsin.',
    }

    orchestration_hint = _orchestration_hint(inferred.get('intent'))
    triage = {'kind': kind, 'reason': triage_reason}
    return {
        **agent_out,
        'command': 'assistant',
        'message': message,
        'goal': goal,
        'intent': inferred.get('intent'),
        'inference': inferred,
        'orchestration_hint': orchestration_hint,
        'triage': triage,
        'assistant_output': _assistant_output_contract(mode='run', triage=triage, ux=ux, orchestration_hint=orchestration_hint),
        'context_budget': {
            'max_tokens': context_pack.get('max_tokens'),
            'used_tokens': context_pack.get('used_tokens'),
            'sections': context_pack.get('sections'),
        },
        'progress': progress,
        'ux': ux,
        'ux_quality': score_ux_output(ux),
    }


def cmd_agent(args: argparse.Namespace) -> dict:
    goal = (args.goal or '').strip()
    if not goal:
        return {'status': 'error', 'command': 'agent', 'errors': ['empty_goal']}

    run_id = args.resume_run_id or f"ARUN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}"
    resumed_state = None
    if args.resume_run_id:
        resumed_state = load_agent_state(str(AGENT_RUNS_DIR), args.resume_run_id)
        if not resumed_state:
            return {'status': 'error', 'command': 'agent', 'errors': ['resume_state_not_found'], 'run_id': args.resume_run_id}

    def _runner(step: str, idx: int, total: int) -> dict:
        parsed = parse_command(step, source='graywolf-agent')
        payload = {
            'goal': f"{goal} | step {idx}/{total}: {step}",
            'agent_goal': goal,
            'agent_step': step,
            'agent_step_index': idx,
            'agent_total_steps': total,
        }
        r = _run([
            PY, '-m', 'core.runtime', 'submit-command',
            '--session-id', args.session_id,
            '--intent', parsed['intent'],
            '--payload', json.dumps(payload, ensure_ascii=False),
            '--source', args.source,
        ])

        parsed_out = None
        if r['stdout']:
            try:
                parsed_out = json.loads(r['stdout'].splitlines()[-1])
            except Exception:
                parsed_out = {'raw': r['stdout']}

        call_status = 'ok' if r['exit_code'] == 0 else 'error'
        submit_status = ((parsed_out or {}).get('status') if isinstance(parsed_out, dict) else None) or ('error' if call_status == 'error' else 'queued')

        if submit_status == 'confirm_required':
            summary = f"Adım {idx}/{total} onay bekliyor (intent={parsed['intent']})."
            approval_request_id = (((parsed_out or {}).get('approval_request') or {}).get('request_id') if isinstance(parsed_out, dict) else None)
            return {
                'status': 'confirm_required',
                'summary': summary,
                'approval_request_id': approval_request_id,
                'intent': parsed['intent'],
                'parse': parsed,
                'result': parsed_out,
                'exec': r,
            }

        task_id = ((parsed_out or {}).get('task') or {}).get('task_id') if isinstance(parsed_out, dict) else None
        if submit_status == 'queued' and task_id:
            tracked = wait_for_task_completion(task_id, processed_dir=str(ROOT / 'tasks' / 'processed'), timeout_seconds=45)
            return {
                'status': tracked.get('status', 'error'),
                'summary': tracked.get('summary', f'Adım {idx}/{total} sonucu belirsiz.'),
                'task_id': task_id,
                'intent': parsed['intent'],
                'parse': parsed,
                'result': parsed_out,
                'tracked': tracked,
                'exec': r,
            }

        summary = f"Adım {idx}/{total} submit sonucu: {submit_status}."
        return {
            'status': 'error' if submit_status in {'error', 'failed', 'blocked', 'timeout'} else submit_status,
            'summary': summary,
            'intent': parsed['intent'],
            'parse': parsed,
            'result': parsed_out,
            'exec': r,
        }

    if args.plan_only:
        plan = build_plan(goal, max_steps=args.max_steps)
        return {
            'status': 'ok',
            'command': 'agent',
            'goal': goal,
            'mode': 'plan_only',
            'plan': plan,
            'ux': {
                'summary': f'Plan üretildi ({len(plan)} adım).',
                'next_step': 'Yürütmek için `graywolf agent --goal "..."` çalıştır.',
            },
        }

    if resumed_state:
        out = run_agent_loop(
            goal,
            step_runner=_runner,
            max_steps=int(resumed_state.get('max_steps') or args.max_steps),
            timeout_retries=2,
            start_index=int(resumed_state.get('next_step_index') or 1),
            existing_plan=list(resumed_state.get('plan') or []),
            existing_trace=list(resumed_state.get('trace') or []),
        )
    else:
        out = run_agent_loop(goal, step_runner=_runner, max_steps=args.max_steps, timeout_retries=2)

    out['command'] = 'agent'
    out['mode'] = 'run'
    out['run_id'] = run_id

    prev_continuity = dict((resumed_state or {}).get('continuity') or {}) if resumed_state else {}
    approved_ids = list(prev_continuity.get('approved_request_ids') or [])
    continuity = {
        'run_id': run_id,
        'resume_count': int(prev_continuity.get('resume_count') or 0) + (1 if resumed_state else 0),
        'pause_count': int(prev_continuity.get('pause_count') or 0) + (1 if out.get('status') == 'confirm_required' else 0),
        'approved_request_ids': approved_ids,
    }
    if out.get('status') == 'confirm_required':
        continuity['last_approval_request_id'] = ((out.get('pause') or {}).get('approval_request_id'))

    out['continuity'] = continuity

    state_payload = {
        'run_id': run_id,
        'goal': goal,
        'session_id': args.session_id,
        'source': args.source,
        'max_steps': args.max_steps,
        'status': out.get('status'),
        'plan': out.get('plan') or [],
        'trace': out.get('trace') or [],
        'pause': out.get('pause') or {},
        'continuity': continuity,
        'next_step_index': int(((out.get('pause') or {}).get('step_index') or 0)) + 1 if out.get('status') == 'confirm_required' else None,
        'final': out.get('final') or {},
    }
    save_agent_state(str(AGENT_RUNS_DIR), run_id, state_payload)
    out['state_file'] = str(AGENT_RUNS_DIR / f"{run_id}.json")

    return out


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

    sp_agent = sub.add_parser('agent', help='Single-agent plan and execute loop')
    sp_agent.add_argument('--goal', required=True)
    sp_agent.add_argument('--max-steps', type=int, default=4)
    sp_agent.add_argument('--source', default='graywolf-agent')
    sp_agent.add_argument('--session-id', default='graywolf-agent')
    sp_agent.add_argument('--plan-only', action='store_true')
    sp_agent.add_argument('--resume-run-id', default='')
    sp_agent.set_defaults(handler=cmd_agent)

    sp_assistant = sub.add_parser('assistant', help='Natural-language assistant entrypoint for agent loop')
    sp_assistant.add_argument('--message', required=True)
    sp_assistant.add_argument('--max-steps', type=int, default=4)
    sp_assistant.add_argument('--source', default='graywolf-assistant')
    sp_assistant.add_argument('--session-id', default='graywolf-assistant')
    sp_assistant.add_argument('--plan-only', action='store_true')
    sp_assistant.set_defaults(handler=cmd_assistant)

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

