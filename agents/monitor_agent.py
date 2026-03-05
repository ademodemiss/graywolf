from dataclasses import dataclass

from monitor.alert import workflow_error_alert
from monitor.status_report import build_status_report


@dataclass
class MonitorAgent:
    def check(self, execution_result: dict | None = None) -> dict:
        status = build_status_report()
        alerts = []

        if execution_result:
            for item in execution_result.get("results", []):
                exit_code = item.get("exit_code")
                if exit_code is not None and int(exit_code) != 0:
                    alerts.append(workflow_error_alert(int(exit_code), item.get("cmd", "")))

        out = {
            "status": "ok" if not alerts else "warning",
            "alerts": alerts,
            "monitor": status,
        }
        return out
