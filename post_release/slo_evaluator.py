import argparse
import json
from pathlib import Path

HB = Path('/home/adem/graywolf/post_release/heartbeat_snapshot.json')
TD = Path('/home/adem/graywolf/post_release/ops_trend_digest.json')
OUT = Path('/home/adem/graywolf/post_release/slo_report.json')


def run_test() -> dict:
    hb = json.loads(HB.read_text(encoding='utf-8')) if HB.exists() else {}
    td = json.loads(TD.read_text(encoding='utf-8')) if TD.exists() else {}
    status = hb.get('status', 'warn')
    anomaly_delta = td.get('drift', {}).get('anomaly_delta', 0)
    if status == 'error' or anomaly_delta > 5:
        compliance = 'fail'
    elif status == 'warn' or anomaly_delta > 0:
        compliance = 'warn'
    else:
        compliance = 'pass'
    out = {'status': 'ok', 'compliance': compliance, 'heartbeat_status': status, 'anomaly_delta': anomaly_delta}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['file'] = str(OUT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--test', action='store_true'); a = p.parse_args()
    print(json.dumps(run_test() if a.test else {'status': 'idle'}, ensure_ascii=False))
