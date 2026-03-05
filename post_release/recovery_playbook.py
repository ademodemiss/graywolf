import argparse
import json
from pathlib import Path

SRC = Path('/home/adem/graywolf/post_release/incident_triage.json')
OUT = Path('/home/adem/graywolf/post_release/recovery_plan.json')


def run_test() -> dict:
    triage = json.loads(SRC.read_text(encoding='utf-8')) if SRC.exists() else {'severity': 'warning'}
    sev = triage.get('severity', 'warning')
    steps_map = {
        'critical': ['operator_run: sudo systemctl status graywolf', 'operator_run: sudo systemctl restart graywolf', 'verify post_release.ops_summary'],
        'warning': ['verify trend digest', 'run guarded restart recommendation'],
        'normal': ['no action'],
    }
    out = {'status': 'ok', 'severity': sev, 'steps': steps_map.get(sev, steps_map['warning'])}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['file'] = str(OUT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
