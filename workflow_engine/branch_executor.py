import argparse
import json


def execute_branch(workflow: dict, context: dict) -> dict:
    branches = workflow.get('branches', [])
    default = workflow.get('default', {'run': 'echo default'})

    chosen = default
    for b in branches:
        cond_key = b.get('if_key')
        cond_val = b.get('if_equals')
        if context.get(cond_key) == cond_val:
            chosen = b
            break

    return {'status': 'ok', 'selected': chosen.get('name', 'default'), 'run': chosen.get('run')}


def run_test() -> dict:
    wf = {
        'branches': [
            {'name': 'premium_path', 'if_key': 'tier', 'if_equals': 'premium', 'run': 'echo premium'},
            {'name': 'basic_path', 'if_key': 'tier', 'if_equals': 'basic', 'run': 'echo basic'},
        ],
        'default': {'name': 'default_path', 'run': 'echo default'}
    }
    out1 = execute_branch(wf, {'tier': 'premium'})
    out2 = execute_branch(wf, {'tier': 'unknown'})
    return {'status': 'ok', 'premium_selected': out1['selected'] == 'premium_path', 'default_selected': out2['selected'] == 'default_path'}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    args = p.parse_args()
    if args.test:
        print(json.dumps(run_test(), ensure_ascii=False))
    else:
        print(json.dumps({'status': 'idle'}, ensure_ascii=False))
