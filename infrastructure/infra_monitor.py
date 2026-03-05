import json

from cluster.cluster_status import get_cluster_status


def collect_cluster_metrics() -> dict:
    cs = get_cluster_status()
    cpu = int(str(cs.get('cluster_load', '0%')).replace('%', '') or 0)
    return {
        'cpu_load': cpu,
        'active_tasks': cs.get('active_tasks', 0),
        'node_count': cs.get('nodes', 0),
        'error_rate': 0,
    }


if __name__ == '__main__':
    print(json.dumps(collect_cluster_metrics(), ensure_ascii=False))
