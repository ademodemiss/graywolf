import datetime
import json
from pathlib import Path


def _read_terminal_entries(log_path: str = "/home/adem/graywolf/logs/terminal.log") -> list[dict]:
    p = Path(log_path)
    if not p.exists():
        return []
    lines = p.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def build_status_report(log_path: str = "/home/adem/graywolf/logs/terminal.log", idle_threshold_minutes: int = 15) -> dict:
    entries = _read_terminal_entries(log_path)
    active_workflows = sum(1 for e in entries if "workflows.runner" in str(e.get("cmd", "")))
    errors_detected = sum(1 for e in entries if int(e.get("exit_code", 0) or 0) != 0)

    last_log_entry = None
    idle_status = True
    if entries:
        last_log_entry = entries[-1].get("ts")
        try:
            last_dt = datetime.datetime.fromisoformat(last_log_entry.replace("Z", "+00:00"))
            now = datetime.datetime.now(datetime.timezone.utc)
            idle_status = (now - last_dt).total_seconds() >= idle_threshold_minutes * 60
        except Exception:
            idle_status = True

    return {
        "active_workflows": active_workflows,
        "last_log_entry": last_log_entry,
        "errors_detected": errors_detected,
        "idle_status": idle_status,
    }


def format_report(report: dict) -> str:
    return (
        "GrayWolf Status Report\n"
        f"• active workflows: {report.get('active_workflows', 0)}\n"
        f"• last log entry: {report.get('last_log_entry')}\n"
        f"• errors detected: {report.get('errors_detected', 0)}\n"
        f"• idle status: {str(report.get('idle_status', True)).lower()}"
    )


def status_report_message(report: dict) -> str:
    return (
        "GRAYWOLF STATUS\n"
        f"active workflows: {report.get('active_workflows', 0)}\n"
        f"last log entry: {report.get('last_log_entry')}\n"
        f"errors detected: {report.get('errors_detected', 0)}\n"
        f"idle status: {str(report.get('idle_status', True)).lower()}"
    )
