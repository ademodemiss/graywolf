import json
import subprocess

from cluster.node_manager import list_nodes, register_node, remove_node


DEFAULT_HOST = '127.0.0.1'
BASE_PORT = 8800


def create_node() -> dict:
    nodes = list_nodes()
    used_ports = {int(n.get('port', 0)) for n in nodes}
    port = BASE_PORT
    while port in used_ports:
        port += 1

    node_id = f'node-{port}'
    proc = subprocess.Popen(['python3', '-m', 'cluster.node_server', '--host', DEFAULT_HOST, '--port', str(port)])
    node = {
        'node_id': node_id,
        'ip': DEFAULT_HOST,
        'port': port,
        'status': 'running',
        'cpu_load': 0,
        'active_tasks': 0,
        'pid': proc.pid,
    }
    register_node(node)
    return {'status': 'created', 'node': node}


def destroy_node(node_id: str) -> dict:
    nodes = list_nodes()
    target = next((n for n in nodes if n.get('node_id') == node_id), None)
    if not target:
        return {'status': 'not_found', 'node_id': node_id}

    pid = target.get('pid')
    if pid:
        try:
            subprocess.run(['kill', str(pid)], check=False)
        except Exception:
            pass

    remove_node(node_id)
    return {'status': 'destroyed', 'node_id': node_id}


if __name__ == '__main__':
    print(json.dumps(create_node(), ensure_ascii=False))
