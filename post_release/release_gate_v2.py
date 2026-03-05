import argparse
import json
from pathlib import Path

TRIAGE = Path('/home/adem/graywolf/post_release/incident_triage.json')
REC = Path('/home/adem/graywolf/post_release/recovery_plan.json')
SLO = Path('/home/adem/graywolf/post_release/slo_report.json')
OUT = Path('/home/adem/graywolf/post_release/release_gate_v2.json')


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}


def run_test() -> dict:
    t = _load(TRIAGE); r = _load(REC); s = _load(SLO)
    if s.get('compliance') == 'fail' or t.get('severity') == 'critical':
        gate = 'fail'
    elif s.get('compliance') == 'warn' or t.get('severity') == 'warning':
        gate = 'warn'
    else:
        gate = 'pass'
    out = {'status': 'ok', 'gate': gate, 'inputs': {'triage': str(TRIAGE), 'recovery': str(REC), 'slo': str(SLO)}}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['file'] = str(OUT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
