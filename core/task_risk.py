import argparse
import json
from pathlib import Path

REPORT = Path('/home/adem/graywolf/reports/task_risk_gate_report.json')


def classify_risk(task: dict) -> str:
    scope = [str(x) for x in task.get('scope', [])]
    ops = ' '.join(task.get('verification_commands', []))
    if any(x in ops for x in ['rm ', 'rebase', 'push', 'checkout -B']) or len(scope) > 5:
        return 'high'
    if any(x in ops for x in ['git commit', 'git add', 'network']) or len(scope) > 2:
        return 'medium'
    return 'low'


def gate_result(task: dict, approved: bool = False) -> dict:
    risk = classify_risk(task)
    blocked = risk == 'high' and not approved
    return {
        'risk_class': risk,
        'permission_gate': {
            'approved': approved,
            'blocked': blocked,
            'reason': 'high_risk_requires_approval' if blocked else 'allowed',
        },
    }


def run_test() -> dict:
    low_task = {
        'id': 'TASK-LOW',
        'scope': ['coding/semantic_search.py'],
        'verification_commands': ['python3 -m py_compile coding/semantic_search.py'],
    }
    high_task = {
        'id': 'TASK-HIGH',
        'scope': ['core/a.py', 'core/b.py', 'core/c.py', 'core/d.py', 'core/e.py', 'core/f.py'],
        'verification_commands': ['git commit -m test'],
    }

    low = gate_result(low_task, approved=False)
    high_blocked = gate_result(high_task, approved=False)
    high_approved = gate_result(high_task, approved=True)

    checks = {
        'low_allowed': not low['permission_gate']['blocked'],
        'high_blocked_without_approval': high_blocked['permission_gate']['blocked'],
        'high_allowed_with_approval': not high_approved['permission_gate']['blocked'],
    }

    out = {
        'status': 'ok' if all(checks.values()) else 'failed',
        'checks': checks,
        'samples': {'low': low, 'high_blocked': high_blocked, 'high_approved': high_approved},
    }
    REPORT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['artifact'] = str(REPORT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
