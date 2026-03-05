import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/home/adem/graywolf/post_release')
PREFIX = 'ops_summary_'
KEEP = 3


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def run_test() -> dict:
    ROOT.mkdir(parents=True, exist_ok=True)

    latest = ROOT / 'ops_summary_latest.json'
    if latest.exists():
        snap = ROOT / f'{PREFIX}{_stamp()}.json'
        snap.write_text(latest.read_text(encoding='utf-8'), encoding='utf-8')

    files = sorted(ROOT.glob(f'{PREFIX}*.json'))
    removed = []
    if len(files) > KEEP:
        for f in files[:-KEEP]:
            removed.append(str(f))
            f.unlink(missing_ok=True)

    remained = [str(p) for p in sorted(ROOT.glob(f'{PREFIX}*.json'))]
    report = {
        'status': 'ok',
        'keep': KEEP,
        'removed_count': len(removed),
        'removed': removed,
        'remaining_count': len(remained),
        'remaining': remained,
    }
    out = ROOT / 'ops_retention_report.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    report['report_file'] = str(out)
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    out = run_test() if args.test else {'status': 'idle'}
    print(json.dumps(out, ensure_ascii=False))
