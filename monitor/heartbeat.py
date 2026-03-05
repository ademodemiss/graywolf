import argparse
from pathlib import Path

from monitor.alert import agent_loop_stopped_alert, idle_alert, workflow_error_alert
from monitor.status_report import build_status_report, format_report, status_report_message
from monitor.telegram_alert import send_telegram_message


def _agent_loop_running(status_file: str = "/home/adem/graywolf/logs/agent_loop.status") -> bool:
    p = Path(status_file)
    if not p.exists():
        return False
    txt = p.read_text(encoding="utf-8").strip().lower()
    return txt == "running"


def run_heartbeat(test: bool = False) -> dict:
    report = build_status_report()
    alerts = []

    if report.get("idle_status"):
        alerts.append(idle_alert(15))

    if not _agent_loop_running():
        alerts.append(agent_loop_stopped_alert())

    # Last-entry workflow error detection
    # If there is any non-zero exit command, emit one summary alert.
    if int(report.get("errors_detected", 0)) > 0:
        alerts.append(workflow_error_alert(-1, "see terminal.log non-zero exit entries"))

    output = {
        "heartbeat_started": True,
        "status_report_generated": True,
        "status_report": report,
        "alerts": alerts,
    }

    print(format_report(report))
    send_telegram_message(status_report_message(report))
    if test:
        print("heartbeat_started")
        print("status_report_generated")

    return output


def main():
    parser = argparse.ArgumentParser(description="GrayWolf heartbeat monitor")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    run_heartbeat(test=args.test)


if __name__ == "__main__":
    main()
