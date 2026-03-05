import json


def parse_workflow(raw: str | dict) -> dict:
    if isinstance(raw, dict):
        wf = raw
    else:
        wf = json.loads(raw)
    return {'steps': wf.get('steps', [])}


if __name__ == '__main__':
    print(json.dumps(parse_workflow('{"steps":[{"run":"echo a"}]}'), ensure_ascii=False))
