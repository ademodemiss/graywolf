import argparse
import json
import subprocess

ANOMALY_WORDS = ['error', 'failed', 'exception', 'traceback', 'denied', 'blocked']


def _journal_tail(lines: int = 80) -> str:
    p = subprocess.run(
        ['journalctl', '-u', 'graywolf', '-n', str(lines), '--no-pager'],
        capture_output=True,
        text=True,
        check=False,
    )
    return p.stdout or ''


def run_test() -> dict:
    text = _journal_tail(80)
    low = text.lower()
    counts = {w: low.count(w) for w in ANOMALY_WORDS}
    total = sum(counts.values())

    if total == 0:
        status = 'ok'
    elif total < 5:
        status = 'warn'
    else:
        status = 'error'

    return {
        'status': status,
        'total_anomalies': total,
        'counts': counts,
        'scanned_lines': len(text.splitlines()),
    }


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    out = run_test() if args.test else {'status': 'idle'}
    print(json.dumps(out, ensure_ascii=False))
