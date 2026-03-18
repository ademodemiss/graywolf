import argparse
import datetime
import json
from pathlib import Path

from core.event_bus import EventBus
from core.event_types import EventTypes

BUS = EventBus()


NODES_DB = Path('/home/adem/graywolf/cluster/nodes.json')


def _load_nodes() -> list[dict]:
    if not NODES_DB.exists():
        return []
    try:
        return json.loads(NODES_DB.read_text(encoding='utf-8'))
    except Exception:
        return []


def _save_nodes(nodes: list[dict]):
    NODES_DB.parent.mkdir(parents=True, exist_ok=True)
    NODES_DB.write_text(json.dumps(nodes, ensure_ascii=False, indent=2), encoding='utf-8')

def get_node(node_id: str) -> dict | None:
    for node in _load_nodes():
        if node.get('node_id') == node_id:
            return node
    return None


def update_node(node_id: str, updates: dict) -> dict | None:
    if not updates:
        return get_node(node_id)
    nodes = _load_nodes()
    updated_node = None
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for idx, node in enumerate(nodes):
        if node.get('node_id') != node_id:
            continue
        node_copy = dict(node)
        node_copy.update(updates)
        node_copy['updated_at'] = now
        nodes[idx] = node_copy
        updated_node = node_copy
        break
    if updated_node:
        _save_nodes(nodes)
        BUS.publish(EventTypes.NODE_UPDATED, {'node_id': node_id, 'status': updated_node.get('status')})
    return updated_node


def register_node(node: dict) -> dict:
    nodes = _load_nodes()
    node_id = node.get('node_id')
    nodes = [n for n in nodes if n.get('node_id') != node_id]
    nodes.append(node)
    _save_nodes(nodes)
    BUS.publish(EventTypes.NODE_JOINED, {'node_id': node.get('node_id'), 'ip': node.get('ip'), 'port': node.get('port')})
    return {'status': 'registered', 'node': node}


def remove_node(node_id: str) -> dict:
    nodes = _load_nodes()
    before = len(nodes)
    nodes = [n for n in nodes if n.get('node_id') != node_id]
    _save_nodes(nodes)
    if before - len(nodes) > 0:
        BUS.publish(EventTypes.NODE_DEAD, {'node_id': node_id})
    return {'status': 'removed', 'count': before - len(nodes)}


def list_nodes() -> list[dict]:
    return _load_nodes()


def main():
    p = argparse.ArgumentParser(description='GrayWolf Cluster Node Manager')
    sub = p.add_subparsers(dest='cmd', required=True)

    r = sub.add_parser('register')
    r.add_argument('--node-id', default='node-local')
    r.add_argument('--ip', default='127.0.0.1')
    r.add_argument('--port', type=int, default=8790)
    r.add_argument('--status', default='running')
    r.add_argument('--cpu-load', type=int, default=0)
    r.add_argument('--active-tasks', type=int, default=0)

    rm = sub.add_parser('remove')
    rm.add_argument('--node-id', required=True)

    sub.add_parser('list')

    args = p.parse_args()
    if args.cmd == 'register':
        print(json.dumps(register_node({
            'node_id': args.node_id,
            'ip': args.ip,
            'port': args.port,
            'status': args.status,
            'cpu_load': args.cpu_load,
            'active_tasks': args.active_tasks,
        }), ensure_ascii=False))
    elif args.cmd == 'remove':
        print(json.dumps(remove_node(args.node_id), ensure_ascii=False))
    else:
        print(json.dumps({'status': 'ok', 'nodes': list_nodes()}, ensure_ascii=False))


if __name__ == '__main__':
    main()
