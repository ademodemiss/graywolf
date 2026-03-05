import datetime
import json
from pathlib import Path

from monitor.telegram_alert import send_telegram_message


def emit_alert(code: str, detail: str, log_dir: str = "/home/adem/graywolf/logs") -> dict:
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    payload = {"ts": ts, "alert": code, "detail": detail}

    log_path = Path(log_dir) / "alerts.log"
    system_log_path = Path(log_dir) / "system.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    line = json.dumps(payload, ensure_ascii=False)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    with open(system_log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    text = f"GRAYWOLF ALERT\n{code}\n{detail}"
    send_telegram_message(text)

    return payload


def idle_alert(minutes_idle: int) -> dict:
    return emit_alert("GRAYWOLF_IDLE_ALERT", f"GRAYWOLF ALERT Agent idle for {minutes_idle} minutes")


def agent_loop_stopped_alert() -> dict:
    return emit_alert("AGENT_LOOP_STOPPED", "agent_loop status is not running")


def workflow_error_alert(exit_code: int, cmd: str) -> dict:
    return emit_alert("WORKFLOW_ERROR", f"GRAYWOLF ERROR workflow execution failed | exit_code={exit_code} cmd={cmd}")
