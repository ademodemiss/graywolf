import json
from cluster.node_manager import list_nodes


def get_cluster_status() -> dict:
    nodes = list_nodes()
    node_count = len(nodes)
    active_tasks = sum(int(n.get('active_tasks', 0)) for n in nodes)
    avg_load = int(sum(int(n.get('cpu_load', 0)) for n in nodes) / node_count) if node_count else 0
    return {
        'nodes': node_count,
        'active_tasks': active_tasks,
        'cluster_load': f'{avg_load}%',
        'node_list': nodes,
    }


if __name__ == '__main__':
    print(json.dumps(get_cluster_status(), ensure_ascii=False))
