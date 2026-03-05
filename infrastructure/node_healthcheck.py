import json
import urllib.request

from cluster.node_manager import list_nodes


def check_nodes() -> dict:
    healthy, unhealthy = [], []
    for n in list_nodes():
        url = f"http://{n['ip']}:{n['port']}/"
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                if r.status == 200:
                    healthy.append(n['node_id'])
                else:
                    unhealthy.append(n['node_id'])
        except Exception:
            unhealthy.append(n['node_id'])
    return {'healthy': healthy, 'unhealthy': unhealthy}


if __name__ == '__main__':
    print(json.dumps(check_nodes(), ensure_ascii=False))
