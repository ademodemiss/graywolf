import argparse
import json
from pathlib import Path

REPORT = Path('/home/adem/graywolf/reports/task_recovery_report.json')


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return {}


def build_recovery_plan(evidence: dict) -> dict:
    final_status = evidence.get('final_status', 'unknown')
    decision = evidence.get('decision', 'unknown')

    if final_status == 'no_changes':
        plan = {'has_plan': False, 'reason': 'no_changes'}
    elif decision == 'committed':
        plan = {
            'has_plan': True,
            'kind': 'post_commit',
            'commands': [
                'git revert <commit_hash>',
                'git checkout -',
                'git branch -D <task-branch>  # optional cleanup',
            ],
        }
    elif 'verify_failed' in final_status or decision == 'blocked':
        plan = {
            'has_plan': True,
            'kind': 'pre_commit_failure',
            'commands': [
                'inspect verification stderr',
                're-run task with --dry-run',
                're-run after fixing scope/dirty tree',
            ],
            'recovery_hint': 'No commit created; safe to retry after cleanup.',
        }
    else:
        plan = {'has_plan': True, 'kind': 'generic', 'commands': ['inspect logs', 'retry guarded']} 

    return {'final_status': final_status, 'decision': decision, 'plan': plan}


def run_test() -> dict:
    # Explicit no_changes scenario (deterministic fixture in-memory)
    no_changes_case = build_recovery_plan({'final_status': 'no_changes', 'decision': 'no_commit'})

    # Real verify-fail evidence
    ev_fail = _load('/home/adem/graywolf/reports/task_TASK-VERIFY-FAIL_git_evidence.json')
    fail_case = build_recovery_plan(ev_fail)

    checks = {
        'no_changes_has_no_plan': no_changes_case['plan'].get('has_plan') is False,
        'verify_fail_has_hint': bool(fail_case['plan'].get('recovery_hint')),
    }

    out = {
        'status': 'ok' if all(checks.values()) else 'failed',
        'checks': checks,
        'cases': {
            'no_changes': no_changes_case,
            'verify_fail': fail_case,
        },
    }
    REPORT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['artifact'] = str(REPORT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
