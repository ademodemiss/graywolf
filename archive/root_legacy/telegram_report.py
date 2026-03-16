#!/usr/bin/env python3
import os, json, requests
from datetime import datetime, timedelta, timezone

TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")
LOG = "/home/adem/graywolf/logs/terminal.log"
WINDOW_MIN = 15
TAIL_LINES = 400 # son satırlardan okur, hafif

def parse_ts(s: str):
    try:
        return datetime.fromisoformat(s)
    except:
        return None

def safe_send(text: str):
    if not (TOKEN and CHAT_ID and requests):
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=15,
        )
        return r.ok
    except Exception as e:
        # Log this error somewhere if possible, for now just print
        print(f"Telegram send error: {e}")
        return False

def main():
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=WINDOW_MIN)

    if not os.path.exists(LOG):
        msg = f"🟡 GrayWolf 15dk Rapor\nAktivite yok (terminal.log bulunamadı)."
        safe_send(msg)
        return

    total = allow = confirm = deny = errors = 0
    recent_cmds = []

    with open(LOG, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()[-TAIL_LINES:]
        for line in lines:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                obj = json.loads(line)
            except:
                continue

            ts = parse_ts(obj.get("ts", ""))
            if not ts:
                continue
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts < cutoff:
                continue

            total += 1
            dec = (obj.get("decision") or "").upper()
            if dec == "ALLOW":
                allow += 1
            elif dec == "CONFIRM":
                confirm += 1
            elif dec == "DENY":
                deny += 1

            exit_code = obj.get("exit_code", 0)
            if isinstance(exit_code, int) and exit_code != 0:
                errors += 1

            cmd = (obj.get("cmd") or "").strip()
            if cmd:
                recent_cmds.append(cmd) # son 3 komut

    last3 = recent_cmds[-3:]
    last3_txt = "\n".join([f"- {c[:120]}" for c in last3]) if last3 else "- (yok)"

    msg = (
        f"🟢 GrayWolf 15dk Rapor\n"
        f"Toplam: {total} | ALLOW:{allow} CONFIRM:{confirm} DENY:{deny} | Hata:{errors}\n"
        f"Son 3 komut:\n{last3_txt}"
    )

    ok = safe_send(msg)
    if not ok: # telegram yoksa en azından dosyaya yaz
        out = "/home/adem/graywolf/status_report.log"
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"[{now.isoformat()}]\n{msg}\n\n")

if __name__ == "__main__":
    main()
