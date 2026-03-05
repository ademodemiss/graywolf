import json

from cluster.node_client import send_task
from cluster.node_manager import list_nodes


def _least_load_node(nodes: list[dict]) -> dict | None:
    if not nodes:
        return None
    return sorted(nodes, key=lambda n: (int(n.get('cpu_load', 9999)), int(n.get('active_tasks', 9999))))[0]


def dispatch_task(task: str) -> dict:
    nodes = list_nodes()
    node = _least_load_node(nodes)
    if not node:
        return {'status': 'error', 'error': 'no_nodes'}
    result = send_task(node, task)
    return {'status': 'ok', 'node': node.get('node_id'), 'result': result}


if __name__ == '__main__':
    print(json.dumps(dispatch_task('echo dispatcher-test'), ensure_ascii=False))
