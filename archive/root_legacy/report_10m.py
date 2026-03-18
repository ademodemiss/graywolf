#!/usr/bin/env python3
import json, os
from datetime import datetime, timedelta, timezone

LOG = "/home/adem/graywolf/logs/terminal.log"
OUT = "/home/adem/graywolf/status_report.log"
WINDOW_MIN = 10

def parse_ts(s: str) -> datetime | None:
    # Example: "2026-03-03T08:53:37.096256+00:00"
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def main():
    if not os.path.exists(LOG):
        return

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=WINDOW_MIN)

    total = allow = confirm = deny = err = 0
    last = None
    last_ts = None

    # Read last ~200 lines to be cheap
    try:
        with open(LOG, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - 200_000), os.SEEK_SET)
            data = f.read().decode("utf-8", errors="ignore").splitlines()
    except Exception:
        return

    for line in data:
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue

        ts = parse_ts(obj.get("ts",""))
        if not ts:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if ts < cutoff:
            continue

        total += 1
        dec = (obj.get("decision") or "").upper()
        if dec == "ALLOW": allow += 1
        elif dec == "CONFIRM": confirm += 1
        elif dec == "DENY": deny += 1

        exit_code = obj.get("exit_code")
        if isinstance(exit_code, int) and exit_code != 0:
            err += 1

        if last_ts is None or ts > last_ts:
            last_ts = ts
            last = obj

    if total == 0:
        msg = f"[{now.isoformat()}] Son {WINDOW_MIN}dk: Aktivite yok."
    else:
        cmd = (last.get("cmd","") if last else "")[:120]
        msg = (
            f"[{now.isoformat()}] Son {WINDOW_MIN}dk: {total} komut | "
            f"ALLOW {allow} / CONFIRM {confirm} / DENY {deny} | "
            f"Hata {err} | Son: {cmd}"
        )

    with open(OUT, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

if __name__ == "__main__":
    main()
