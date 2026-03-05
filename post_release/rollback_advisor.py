import argparse
import json
from pathlib import Path

TRIAGE = Path('/home/adem/graywolf/post_release/incident_triage.json')
GATE = Path('/home/adem/graywolf/post_release/release_gate_v2.json')
OUT = Path('/home/adem/graywolf/post_release/rollback_advisor.json')


def _read(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return default


def run_test() -> dict:
    t = _read(TRIAGE, {'severity': 'warning'})
    g = _read(GATE, {'gate': 'warn'})
    sev = t.get('severity', 'warning')
    gate = g.get('gate', 'warn')

    matrix = {
        ('critical', 'fail'): 'full_rollback',
        ('critical', 'warn'): 'partial_rollback',
        ('warning', 'fail'): 'partial_rollback',
        ('warning', 'warn'): 'hold_and_monitor',
        ('normal', 'pass'): 'continue',
    }
    action = matrix.get((sev, gate), 'hold_and_monitor')

    out = {'status': 'ok', 'severity': sev, 'gate': gate, 'recommended_action': action}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['file'] = str(OUT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
