import datetime
import json
from pathlib import Path


TERMINAL_LOG = "/home/adem/graywolf/logs/terminal.log"
AGENT_STATUS_FILE = "/home/adem/graywolf/logs/agent_loop.status"


def _parse_ts(ts: str):
    if not ts:
        return None
    try:
        return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _read_terminal_entries(path: str = TERMINAL_LOG) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def get_last_logs(n: int = 20) -> list[dict]:
    return _read_terminal_entries()[-n:]


def get_last_workflows(n: int = 10) -> list[dict]:
    entries = _read_terminal_entries()
    wf = [e for e in entries if "workflows.runner" in str(e.get("cmd", ""))]
    return wf[-n:]


def get_idle_status(idle_minutes: int = 15) -> dict:
    entries = _read_terminal_entries()
    if not entries:
        return {"idle": True, "idle_minutes": idle_minutes, "last_log_ts": None}

    last_ts = entries[-1].get("ts")
    last_dt = _parse_ts(last_ts)
    if not last_dt:
        return {"idle": True, "idle_minutes": idle_minutes, "last_log_ts": last_ts}

    now = datetime.datetime.now(datetime.timezone.utc)
    diff_minutes = int((now - last_dt).total_seconds() // 60)
    return {"idle": diff_minutes >= idle_minutes, "idle_minutes": max(diff_minutes, 0), "last_log_ts": last_ts}


def get_error_count(last_hours: int = 24) -> dict:
    entries = _read_terminal_entries()
    total_errors = sum(1 for e in entries if int(e.get("exit_code", 0) or 0) != 0)

    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=last_hours)
    recent_errors = 0
    for e in entries:
        if int(e.get("exit_code", 0) or 0) == 0:
            continue
        ts = _parse_ts(e.get("ts"))
        if ts and ts >= cutoff:
            recent_errors += 1

    return {"errors_24h": recent_errors, "errors_total": total_errors}


def get_agent_status() -> str:
    p = Path(AGENT_STATUS_FILE)
    if not p.exists():
        return "unknown"
    txt = p.read_text(encoding="utf-8").strip().lower()
    if txt in {"running", "stopped"}:
        return txt
    return "unknown"


def build_status_payload() -> dict:
    idle = get_idle_status(15)
    errors = get_error_count(24)
    payload = {
        "agent_status": get_agent_status(),
        "idle": idle["idle"],
        "idle_minutes": idle["idle_minutes"],
        "last_log_ts": idle["last_log_ts"],
        "errors_24h": errors["errors_24h"],
        "errors_total": errors["errors_total"],
        "last_logs": get_last_logs(20),
        "last_workflows": get_last_workflows(10),
    }
    return payload
