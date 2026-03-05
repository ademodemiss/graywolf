import argparse
import json
from pathlib import Path

CUR = Path('/home/adem/graywolf/post_release/heartbeat_snapshot.json')
PREV = Path('/home/adem/graywolf/post_release/heartbeat_snapshot.prev.json')
OUT = Path('/home/adem/graywolf/post_release/ops_trend_digest.json')


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def run_test() -> dict:
    cur = _load(CUR)
    prev = _load(PREV)

    if not cur:
        cur = {
            'status': 'warn',
            'journal_total_anomalies': 0,
            'service_state': 'unknown',
            'checks': 0,
        }

    drift = {
        'status_changed': cur.get('status') != prev.get('status') if prev else False,
        'service_state_changed': cur.get('service_state') != prev.get('service_state') if prev else False,
        'anomaly_delta': int(cur.get('journal_total_anomalies', 0)) - int(prev.get('journal_total_anomalies', 0) if prev else 0),
    }

    out = {'status': 'ok', 'current': cur, 'previous_exists': bool(prev), 'drift': drift}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    PREV.write_text(json.dumps(cur, ensure_ascii=False, indent=2), encoding='utf-8')
    out['file'] = str(OUT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    result = run_test() if args.test else {'status': 'idle'}
    print(json.dumps(result, ensure_ascii=False))
