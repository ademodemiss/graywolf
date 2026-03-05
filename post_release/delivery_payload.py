import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from post_release.delivery_readiness import run_test as readiness_test
from post_release.ops_summary import run_test as ops_summary_test

OUT = Path('/home/adem/graywolf/post_release/delivery_payload.json')


def run_test() -> dict:
    readiness = readiness_test()
    summary = ops_summary_test()

    payload = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'level': 'WARN' if summary.get('status') == 'warn' else 'ERROR' if summary.get('status') == 'error' else 'INFO',
        'title': 'GrayWolf Ops Delivery Probe',
        'message': f"ops_status={summary.get('status')} channels_ready={sum(1 for c in readiness.get('channels', []) if c.get('status') == 'ready')}",
        'meta': {
            'ops_status': summary.get('status'),
            'channels': readiness.get('channels', []),
            'journal_total_anomalies': summary.get('journal_anomaly', {}).get('total_anomalies', 0),
        },
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'status': 'ok', 'payload_file': str(OUT), 'payload': payload}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    out = run_test() if args.test else {'status': 'idle'}
    print(json.dumps(out, ensure_ascii=False))
