import argparse
import json
import urllib.request


def send_task(node: dict, task: str) -> dict:
    url = f"http://{node['ip']}:{node['port']}/task"
    body = json.dumps({'task': task}).encode('utf-8')
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode('utf-8', errors='replace'))
    return payload


def main():
    p = argparse.ArgumentParser(description='GrayWolf Node Client')
    p.add_argument('--ip', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8790)
    p.add_argument('--task', required=True)
    args = p.parse_args()

    out = send_task({'ip': args.ip, 'port': args.port}, args.task)
    print(json.dumps(out, ensure_ascii=False))


if __name__ == '__main__':
    main()
