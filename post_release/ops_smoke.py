import argparse
import json
import sys

from post_release.alerts import send_alert
from post_release.ops_monitor import run_monitor


def run_test() -> dict:
    mon = run_monitor()
    alert = send_alert(
        level='WARN' if mon.get('status') == 'warn' else 'ERROR' if mon.get('status') == 'error' else 'INFO',
        title='ops_smoke',
        message=f"ops status={mon.get('status')}",
        meta={'checks': len(mon.get('checks', []))},
        dry_delivery=True,
    )
    return {'status': mon.get('status', 'error'), 'monitor': mon, 'alert': alert}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    out = run_test() if args.test else {'status': 'idle'}
    print(json.dumps(out, ensure_ascii=False))
    if args.test and out.get('status') == 'error':
        sys.exit(1)
