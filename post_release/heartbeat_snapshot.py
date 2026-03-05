import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from post_release.ops_summary import run_test as run_ops_summary

OUT = Path('/home/adem/graywolf/post_release/heartbeat_snapshot.json')


def run_test() -> dict:
    summary = run_ops_summary()
    snapshot = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'status': summary.get('status', 'warn'),
        'journal_total_anomalies': summary.get('journal_anomaly', {}).get('total_anomalies', 0),
        'service_state': summary.get('service_snapshot', {}).get('service', {}).get('is_active', 'unknown'),
        'checks': len(summary.get('ops_monitor', {}).get('checks', [])),
    }
    OUT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'status': 'ok', 'snapshot': snapshot, 'file': str(OUT)}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    out = run_test() if args.test else {'status': 'idle'}
    print(json.dumps(out, ensure_ascii=False))
