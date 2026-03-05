import argparse
import json
from pathlib import Path

from post_release.alerts import send_alert

PAYLOAD = Path('/home/adem/graywolf/post_release/delivery_payload.json')
OUT = Path('/home/adem/graywolf/post_release/delivery_dispatch_result.json')


def run_test() -> dict:
    if not PAYLOAD.exists():
        return {'status': 'failed', 'reason': 'payload_missing', 'payload': str(PAYLOAD)}

    data = json.loads(PAYLOAD.read_text(encoding='utf-8'))
    result = send_alert(
        level=data.get('level', 'INFO'),
        title=data.get('title', 'delivery-probe'),
        message=data.get('message', ''),
        meta=data.get('meta', {}),
        dry_delivery=True,
    )

    out = {
        'status': 'ok',
        'dispatch': result,
        'input_payload': str(PAYLOAD),
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['output'] = str(OUT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    res = run_test() if args.test else {'status': 'idle'}
    print(json.dumps(res, ensure_ascii=False))
