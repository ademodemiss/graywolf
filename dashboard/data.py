import datetime
import json
from pathlib import Path


TERMINAL_LOG = "/home/adem/graywolf/logs/terminal.log"
AGENT_STATUS_FILE = "/home/adem/graywolf/logs/agent_loop.status"
REPLAN_BRIDGE_LOG = "/home/adem/graywolf/logs/self_improve_replan.log"
LEARNING_RECOVERY_LOG = "/home/adem/graywolf/logs/learning_recovery.log"
LEARNING_RECOVERY_SUGGESTIONS = "/home/adem/graywolf/logs/learning_recovery_suggestions.json"
LEARNING_RECOVERY_INSIGHTS = "/home/adem/graywolf/logs/learning_recovery_insights.json"
LEARNING_RECOVERY_ALERTS = "/home/adem/graywolf/logs/learning_recovery_alerts.log"
LEARNING_RECOVERY_TREND = "/home/adem/graywolf/logs/learning_recovery_trend.log"


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


def _read_replan_entries(path: str = REPLAN_BRIDGE_LOG) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def _read_learning_recovery_entries(limit: int = 5, path: str = LEARNING_RECOVERY_LOG) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    entries: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except Exception:
            continue
    return entries[-limit:]


def _read_learning_recovery_alerts(limit: int = 5, path: str = LEARNING_RECOVERY_ALERTS) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    entries: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except Exception:
            continue
    return entries[-limit:]


def _read_learning_recovery_trend(limit: int = 5, path: str = LEARNING_RECOVERY_TREND) -> dict:
    p = Path(path)
    if not p.exists():
        return {"latest": None, "history": []}
    entries: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except Exception:
            continue
    history = entries[-limit:] if limit else entries
    latest = history[-1] if history else None
    return {"latest": latest, "history": history}


def _read_learning_recovery_suggestions(path: str = LEARNING_RECOVERY_SUGGESTIONS) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _read_learning_recovery_insights(path: str = LEARNING_RECOVERY_INSIGHTS) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _compute_replan_processing(entries: list[dict]) -> dict:
    processed_count = sum(1 for entry in entries if entry.get("processed_by_phase265"))
    pending_count = sum(
        1
        for entry in entries
        if (entry.get("approval_request") or {}).get("status") == "GRANTED"
        and not entry.get("processed_by_phase265")
    )

    latencies: list[float] = []
    for entry in entries:
        approval = entry.get("approval_request") or {}
        created = _parse_ts(approval.get("created_at"))
        granted = _parse_ts(approval.get("granted_at"))
        if created and granted:
            latencies.append((granted - created).total_seconds())

    if latencies:
        latency_info = {
            "count": len(latencies),
            "avg_seconds": sum(latencies) / len(latencies),
            "max_seconds": max(latencies),
            "long_count": sum(1 for value in latencies if value > 120),
            "latest_seconds": latencies[-1],
        }
    else:
        latency_info = {
            "count": 0,
            "avg_seconds": None,
            "max_seconds": None,
            "long_count": 0,
            "latest_seconds": None,
        }

    return {
        "processed": processed_count,
        "pending": pending_count,
        "approval_latency": latency_info,
        "approval_latency_threshold_seconds": 120,
    }


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


def get_replan_summary(log_path: str = REPLAN_BRIDGE_LOG) -> dict:
    entries = _read_replan_entries(log_path)
    if not entries:
        return {"exists": False, "entries": 0}
    last = entries[-1]
    analysis = last.get("analysis") or {}
    return {
        "exists": True,
        "entries": len(entries),
        "latest_event": last.get("event"),
        "latest_ts": last.get("ts"),
        "latest_status": analysis.get("status"),
        "approval_request": last.get("approval_request"),
    }


def get_replan_processing_info(log_path: str = REPLAN_BRIDGE_LOG) -> dict:
    entries = _read_replan_entries(log_path)
    if not entries:
        return {
            "processed": 0,
            "pending": 0,
            "approval_latency": {
                "count": 0,
                "avg_seconds": None,
                "max_seconds": None,
                "long_count": 0,
                "latest_seconds": None,
            },
            "approval_latency_threshold_seconds": 120,
        }
    return _compute_replan_processing(entries)


def get_replan_recent_entries(log_path: str = REPLAN_BRIDGE_LOG, limit: int = 5) -> list[dict]:
    entries = _read_replan_entries(log_path)
    if not entries:
        return []
    return entries[-limit:]


def build_status_payload() -> dict:
    idle = get_idle_status(15)
    errors = get_error_count(24)
    learning_recovery_suggestions = _read_learning_recovery_suggestions()
    learning_recovery_entries = _read_learning_recovery_entries()
    learning_recovery_alerts = _read_learning_recovery_alerts()
    learning_recovery_trend = _read_learning_recovery_trend()
    payload = {
        "agent_status": get_agent_status(),
        "idle": idle["idle"],
        "idle_minutes": idle["idle_minutes"],
        "last_log_ts": idle["last_log_ts"],
        "errors_24h": errors["errors_24h"],
        "errors_total": errors["errors_total"],
        "last_logs": get_last_logs(20),
        "last_workflows": get_last_workflows(10),
        "replan_bridge": get_replan_summary(),
        "replan_bridge_entries": get_replan_recent_entries(),
        "replan_bridge_processing": get_replan_processing_info(),
        "learning_recovery": {
            "suggestions": learning_recovery_suggestions,
            "log": learning_recovery_entries,
            "insights": _read_learning_recovery_insights(),
            "alerts": {
                "latest": learning_recovery_alerts[-1] if learning_recovery_alerts else None,
                "history": learning_recovery_alerts,
            },
            "trend": learning_recovery_trend,
        },
    }
    return payload
