import argparse
import json
from pathlib import Path

SRC = Path('/home/adem/graywolf/post_release/release_gate_v2.json')
OUT = Path('/home/adem/graywolf/post_release/canary_gate.json')


def run_test() -> dict:
    gate = 'warn'
    if SRC.exists():
        try:
            gate = json.loads(SRC.read_text(encoding='utf-8')).get('gate', 'warn')
        except Exception:
            gate = 'warn'

    allow = gate in {'pass', 'warn'}
    scope = 'small' if allow else 'none'
    out = {
        'status': 'ok',
        'gate': gate,
        'allow_canary': allow,
        'recommended_scope': scope,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['file'] = str(OUT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
