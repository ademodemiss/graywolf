import json
import urllib.request


with urllib.request.urlopen('http://127.0.0.1:8792/system/metrics', timeout=5) as resp:
    data = json.loads(resp.read().decode('utf-8', errors='replace'))

required = ['queue_depth', 'retry_rate', 'dead_letter_rate', 'active_nodes']
print(json.dumps({'ok': all(k in data for k in required), 'data': data}, ensure_ascii=False))
