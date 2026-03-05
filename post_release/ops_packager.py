import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

SRC_FILES = [
    '/home/adem/graywolf/post_release/incident_triage.json',
    '/home/adem/graywolf/post_release/recovery_plan.json',
    '/home/adem/graywolf/post_release/slo_report.json',
    '/home/adem/graywolf/post_release/release_gate_v2.json',
    '/home/adem/graywolf/post_release/incident_timeline.json',
]
OUT = Path('/home/adem/graywolf/post_release/ops_report_bundle.json')


def run_test() -> dict:
    payload = {'version': 'v2', 'ts': datetime.now(timezone.utc).isoformat(), 'items': {}}
    hasher = hashlib.sha256()
    for p in SRC_FILES:
        path = Path(p)
        if path.exists():
            raw = path.read_bytes()
            payload['items'][path.name] = json.loads(raw.decode('utf-8'))
            hasher.update(raw)
        else:
            payload['items'][path.name] = {'status': 'missing'}
            hasher.update(path.name.encode('utf-8'))
    payload['checksum_sha256'] = hasher.hexdigest()
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'status': 'ok', 'file': str(OUT), 'checksum_sha256': payload['checksum_sha256']}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
