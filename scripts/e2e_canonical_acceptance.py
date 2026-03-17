#!/usr/bin/env python3
"""Graywolf v2 E2E Canonical Acceptance Suite (Job 5)."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

from core.approval import ApprovalManager, ApprovalState
from monitor.approval_callback_router import ApprovalCallbackRouter

ROOT = Path('/home/adem/graywolf')
PY = Path('/home/adem/.openclaw/workspace/.venv/bin/python')
REPORT = ROOT / 'reports' / 'e2e_canonical_acceptance_latest.md'


def _run(cmd: list[str]) -> tuple[int, dict | None, str, str]:
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    out = (p.stdout or '').strip()
    parsed = None
    if out:
        try:
            parsed = json.loads(out.splitlines()[-1])
        except Exception:
            parsed = None
    return p.returncode, parsed, out, (p.stderr or '').strip()


def scenario_1_command_to_task() -> tuple[bool, dict]:
    cmd = [
        str(PY), '-m', 'core.runtime', 'submit-command',
        '--session-id', 'acceptance',
        '--intent', 'healthcheck',
        '--payload', '{"goal":"acceptance scenario1"}',
        '--source', 'acceptance-suite',
    ]
    rc, parsed, out, err = _run(cmd)
    ok = rc == 0 and isinstance(parsed, dict) and parsed.get('status') == 'queued'
    task_file = (((parsed or {}).get('artifacts') or {}).get('queued_task_file'))
    if task_file:
        ok = ok and Path(task_file).exists()

    return ok, {
        'rc': rc,
        'status': (parsed or {}).get('status') if isinstance(parsed, dict) else None,
        'task_file': task_file,
        'stderr': err,
    }


def scenario_2_approval_callback() -> tuple[bool, dict]:
    mgr = ApprovalManager()
    router = ApprovalCallbackRouter()

    req, _msg = mgr.evaluate_command('mv /tmp/a /tmp/b', requested_by='acceptance-suite')
    if not req:
        return False, {'error': 'request_not_created'}

    router.handle_callback(f'approval.grant:{req.request_id}', actor='acceptance-suite')
    final = mgr.wait_for_status(req.request_id, target={ApprovalState.GRANTED}, timeout_seconds=3)

    ok = bool(final and final.status == ApprovalState.GRANTED)
    return ok, {
        'request_id': req.request_id,
        'final_status': final.status.value if final else None,
    }


def scenario_3_failure_recovery() -> tuple[bool, dict]:
    # failure: invalid payload json
    bad_cmd = [
        str(PY), '-m', 'core.runtime', 'submit-command',
        '--session-id', 'acceptance',
        '--intent', 'risk_summary',
        '--payload', '{bad-json',
        '--source', 'acceptance-suite',
    ]
    rc_bad, parsed_bad, _out_bad, _err_bad = _run(bad_cmd)
    bad_is_error = isinstance(parsed_bad, dict) and parsed_bad.get('status') == 'error'

    # recovery: corrected command
    good_cmd = [
        str(PY), '-m', 'core.runtime', 'submit-command',
        '--session-id', 'acceptance',
        '--intent', 'risk_summary',
        '--payload', '{"goal":"acceptance recovery"}',
        '--source', 'acceptance-suite',
    ]
    rc_good, parsed_good, _out_good, err_good = _run(good_cmd)
    recovered = rc_good == 0 and isinstance(parsed_good, dict) and parsed_good.get('status') == 'queued'

    ok = bad_is_error and recovered
    return ok, {
        'bad_rc': rc_bad,
        'bad_status': (parsed_bad or {}).get('status') if isinstance(parsed_bad, dict) else None,
        'good_rc': rc_good,
        'good_status': (parsed_good or {}).get('status') if isinstance(parsed_good, dict) else None,
        'good_stderr': err_good,
    }


def main() -> int:
    s1_ok, s1 = scenario_1_command_to_task()
    s2_ok, s2 = scenario_2_approval_callback()
    s3_ok, s3 = scenario_3_failure_recovery()

    overall = s1_ok and s2_ok and s3_ok
    lines = [
        '# E2E Canonical Acceptance Report',
        '',
        f'- ts: {datetime.now().isoformat()}',
        f'- overall: {"PASS" if overall else "FAIL"}',
        '',
        '## Scenario 1 — command -> task -> report artifact',
        f'- status: {"PASS" if s1_ok else "FAIL"}',
        f'- detail: `{json.dumps(s1, ensure_ascii=False)}`',
        '',
        '## Scenario 2 — approval required -> callback -> continue',
        f'- status: {"PASS" if s2_ok else "FAIL"}',
        f'- detail: `{json.dumps(s2, ensure_ascii=False)}`',
        '',
        '## Scenario 3 — failure -> recovery -> final result',
        f'- status: {"PASS" if s3_ok else "FAIL"}',
        f'- detail: `{json.dumps(s3, ensure_ascii=False)}`',
        '',
    ]

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text('\n'.join(lines), encoding='utf-8')
    print(str(REPORT))
    return 0 if overall else 1


if __name__ == '__main__':
    raise SystemExit(main())
