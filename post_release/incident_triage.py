import argparse
import json
from pathlib import Path

SRC = Path('/home/adem/graywolf/post_release/ops_summary_latest.json')
OUT = Path('/home/adem/graywolf/post_release/incident_triage.json')


def run_test() -> dict:
    data = {}
    if SRC.exists():
        data = json.loads(SRC.read_text(encoding='utf-8'))
    status = data.get('status', 'warn')
    if status == 'error':
        sev = 'critical'
    elif status == 'warn':
        sev = 'warning'
    else:
        sev = 'normal'
    actions = {
        'critical': ['check service state', 'inspect journal anomalies', 'trigger guarded recovery plan'],
        'warning': ['review trend digest', 'verify delivery readiness'],
        'normal': ['continue monitoring'],
    }[sev]
    out = {'status': 'ok', 'severity': sev, 'actions': actions}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['file'] = str(OUT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
