import argparse
import json
from pathlib import Path

from post_release.ops_monitor import run_monitor
from post_release.journal_anomaly import run_test as run_journal
from post_release.service_snapshot import run_test as run_service

OUT = Path('/home/adem/graywolf/post_release/ops_summary_latest.json')


def _rollup(parts: list[str]) -> str:
    if 'error' in parts:
        return 'error'
    if 'warn' in parts:
        return 'warn'
    return 'ok'


def run_test() -> dict:
    mon = run_monitor()
    jour = run_journal()
    svc = run_service()
    status = _rollup([mon.get('status', 'warn'), jour.get('status', 'warn'), svc.get('status', 'warn')])
    out = {
        'status': status,
        'ops_monitor': mon,
        'journal_anomaly': jour,
        'service_snapshot': svc,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['artifact'] = str(OUT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    result = run_test() if args.test else {'status': 'idle'}
    print(json.dumps(result, ensure_ascii=False))
