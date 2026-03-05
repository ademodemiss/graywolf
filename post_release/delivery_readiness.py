import argparse
import json
import os
from pathlib import Path

OUT = Path('/home/adem/graywolf/post_release/delivery_readiness.json')


def run_test() -> dict:
    tg_ready = bool(os.getenv('GW_TELEGRAM_BOT_TOKEN') and os.getenv('GW_TELEGRAM_CHAT_ID'))
    wh_ready = bool(os.getenv('GW_WEBHOOK_URL'))

    channels = [
        {'channel': 'telegram', 'status': 'ready' if tg_ready else 'skipped', 'reason': 'env_ok' if tg_ready else 'missing_env'},
        {'channel': 'webhook', 'status': 'ready' if wh_ready else 'skipped', 'reason': 'env_ok' if wh_ready else 'missing_env'},
    ]

    status = 'ok' if any(c['status'] == 'ready' for c in channels) else 'warn'
    out = {'status': status, 'channels': channels}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    out['file'] = str(OUT)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    result = run_test() if args.test else {'status': 'idle'}
    print(json.dumps(result, ensure_ascii=False))
