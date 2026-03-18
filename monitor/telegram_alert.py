import argparse
import datetime
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


def _write_system_log(text: str, log_dir: str = "/home/adem/graywolf/logs"):
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    path = Path(log_dir) / "system.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": ts, "event": text}, ensure_ascii=False) + "\n")


def send_telegram_message(text: str, reply_markup: dict | None = None) -> dict:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    if not token or not chat_id:
        _write_system_log("TELEGRAM_NOT_CONFIGURED")
        return {"status": "skipped", "reason": "TELEGRAM_NOT_CONFIGURED"}

    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=payload_data, method="POST")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return {"status": "sent", "http_status": getattr(resp, "status", 200), "response": body[:500]}
    except urllib.error.HTTPError as e:
        _write_system_log(f"TELEGRAM_SEND_ERROR status={e.code}")
        return {"status": "error", "error": f"http_{e.code}"}
    except Exception as e:
        _write_system_log(f"TELEGRAM_SEND_ERROR {e}")
        return {"status": "error", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="GrayWolf Telegram alert sender")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    if args.test:
        send_telegram_message("GRAYWOLF TEST telegram alert")
        print("telegram_message_sent")


if __name__ == "__main__":
    main()
