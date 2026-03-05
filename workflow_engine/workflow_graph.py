import json


def build_graph(workflow: dict) -> dict:
    steps = workflow.get('steps', [])
    edges = []
    for i in range(len(steps) - 1):
        edges.append({'from': i, 'to': i + 1})
    return {'nodes': len(steps), 'edges': edges}


if __name__ == '__main__':
    print(json.dumps(build_graph({'steps':[{'run':'a'},{'run':'b'}]}), ensure_ascii=False))
