import argparse
import json

from cluster.node_manager import list_nodes
from infrastructure.infra_config import get_config
from infrastructure.infra_monitor import collect_cluster_metrics
from infrastructure.node_provisioner import create_node, destroy_node


def evaluate_once() -> dict:
    cfg = get_config()
    metrics = collect_cluster_metrics()
    nodes = list_nodes()
    node_count = len(nodes)
    actions = []

    if metrics['cpu_load'] > cfg['cpu_scale_up'] and node_count < cfg['max_nodes']:
        actions.append(create_node())
    elif metrics['cpu_load'] < cfg['cpu_scale_down'] and node_count > cfg['min_nodes']:
        # remove the last non-local node first
        victim = next((n for n in reversed(nodes) if n.get('node_id') != 'node-local'), None)
        if victim:
            actions.append(destroy_node(victim['node_id']))

    return {'status': 'ok', 'metrics': metrics, 'actions': actions, 'node_count': len(list_nodes())}


def run_test() -> dict:
    up = evaluate_once()
    # simulate high load
    fake_high = {'cpu_load': 95}
    actions = []
    if len(list_nodes()) < get_config()['max_nodes']:
        actions.append(create_node())
    # simulate low load and scale down back
    extra = [n for n in list_nodes() if n.get('node_id') != 'node-local']
    down_actions = []
    if extra:
        down_actions.append(destroy_node(extra[-1]['node_id']))
    return {'status': 'ok', 'scale_up': actions, 'scale_down': down_actions, 'initial': up}


def main():
    p = argparse.ArgumentParser(description='GrayWolf Auto Scaler')
    p.add_argument('--test', action='store_true')
    args = p.parse_args()

    if args.test:
        print(json.dumps(run_test(), ensure_ascii=False))
        return

    print(json.dumps(evaluate_once(), ensure_ascii=False))


if __name__ == '__main__':
    main()
