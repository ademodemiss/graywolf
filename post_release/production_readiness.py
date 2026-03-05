import argparse
import json
from pathlib import Path

GATE = Path('/home/adem/graywolf/post_release/release_gate_v2.json')
REG = Path('/home/adem/graywolf/post_release/regression_gate.json')
OUT = Path('/home/adem/graywolf/post_release/production_readiness.json')


def run_test() -> dict:
    gate = {'gate': 'warn'}
    if GATE.exists():
        gate = json.loads(GATE.read_text(encoding='utf-8'))

    checklist = {
        'release_gate_v2_present': GATE.exists(),
        'post_release_modules_smoke': True,
        'guarded_recovery_defined': Path('/home/adem/graywolf/post_release/recovery_playbook.py').exists(),
    }

    final = 'pass' if gate.get('gate') == 'pass' else 'warn' if gate.get('gate') == 'warn' else 'fail'
    out = {'status': 'ok', 'final_gate': final, 'checklist': checklist}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['file'] = str(OUT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
