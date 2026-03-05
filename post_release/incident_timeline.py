import argparse
import json
from pathlib import Path

LOG = Path('/home/adem/graywolf/logs/terminal.log')
OUT = Path('/home/adem/graywolf/post_release/incident_timeline.json')


def run_test() -> dict:
    events = []
    if LOG.exists():
        lines = LOG.read_text(encoding='utf-8').splitlines()[-120:]
        for line in lines:
            try:
                obj = json.loads(line)
            except Exception:
                continue
            events.append({
                'ts': obj.get('ts'),
                'cmd': obj.get('cmd'),
                'exit_code': obj.get('exit_code'),
                'decision': obj.get('decision'),
            })
    out = {'status': 'ok', 'count': len(events), 'events': events[-50:]}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['file'] = str(OUT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
