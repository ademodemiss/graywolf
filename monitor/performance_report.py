import json

from monitor.metrics_collector import collect_metrics


def generate_report() -> str:
    m = collect_metrics()
    return (
        'GRAYWOLF PERFORMANCE REPORT\n'
        f"cpu_load: {m.get('cpu_load')}\n"
        f"memory_usage: {m.get('memory_usage')}\n"
        f"node_count: {m.get('node_count')}\n"
        f"active_tasks: {m.get('active_tasks')}\n"
        f"error_rate: {m.get('error_rate')}"
    )


if __name__ == '__main__':
    print(json.dumps({'report': generate_report()}, ensure_ascii=False))
