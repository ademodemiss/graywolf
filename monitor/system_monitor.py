import json

from monitor.alert_manager import evaluate_alerts
from monitor.metrics_collector import collect_metrics


def monitor_system() -> dict:
    m = collect_metrics()
    return {'metrics': m, 'alerts': evaluate_alerts(m)}


if __name__ == '__main__':
    print(json.dumps(monitor_system(), ensure_ascii=False))
