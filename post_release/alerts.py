import json
import os
import urllib.request


def _post_json(url: str, payload: dict, timeout: int = 3) -> tuple[bool, str]:
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return (200 <= resp.status < 300), f'http_{resp.status}'
    except Exception as e:
        return False, str(e)


def send_alert(level: str, title: str, message: str, meta: dict | None = None, dry_delivery: bool = False) -> dict:
    payload = {
        'level': level,
        'title': title,
        'message': message,
        'meta': meta or {},
    }

    print(json.dumps({'alert_stdout': payload}, ensure_ascii=False))

    deliveries = []

    token = os.getenv('GW_TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('GW_TELEGRAM_CHAT_ID')
    if token and chat_id:
        if dry_delivery:
            deliveries.append({'channel': 'telegram', 'status': 'delivery_skipped', 'reason': 'dry_delivery'})
        else:
            tg_url = f'https://api.telegram.org/bot{token}/sendMessage'
            ok, reason = _post_json(tg_url, {'chat_id': chat_id, 'text': f'[{level}] {title}\n{message}'})
            deliveries.append({'channel': 'telegram', 'status': 'sent' if ok else 'delivery_skipped', 'reason': reason})
    else:
        deliveries.append({'channel': 'telegram', 'status': 'delivery_skipped', 'reason': 'missing_env'})

    webhook = os.getenv('GW_WEBHOOK_URL')
    if webhook:
        if dry_delivery:
            deliveries.append({'channel': 'webhook', 'status': 'delivery_skipped', 'reason': 'dry_delivery'})
        else:
            ok, reason = _post_json(webhook, payload)
            deliveries.append({'channel': 'webhook', 'status': 'sent' if ok else 'delivery_skipped', 'reason': reason})
    else:
        deliveries.append({'channel': 'webhook', 'status': 'delivery_skipped', 'reason': 'missing_env'})

    return {'status': 'ok', 'deliveries': deliveries, 'payload': payload}
