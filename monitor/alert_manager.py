import json


def evaluate_alerts(metrics: dict) -> list[str]:
    alerts = []
    if metrics.get('node_count', 0) == 0:
        alerts.append('node_down')
    if metrics.get('active_tasks', 0) > 100:
        alerts.append('queue_overflow')
    if metrics.get('error_rate', 0) > 50:
        alerts.append('error_spike')
    return alerts


if __name__ == '__main__':
    print(json.dumps({'alerts': evaluate_alerts({'node_count': 1})}, ensure_ascii=False))
