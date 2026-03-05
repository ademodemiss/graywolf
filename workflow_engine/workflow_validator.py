import json

BLOCKED = ['rm -rf', 'shutdown', 'reboot']


def validate_workflow(workflow: dict) -> dict:
    issues = []
    for i, step in enumerate(workflow.get('steps', []), start=1):
        cmd = str(step.get('run', ''))
        for b in BLOCKED:
            if b in cmd:
                issues.append(f'step_{i}_blocked:{b}')
    return {'valid': len(issues) == 0, 'issues': issues}


if __name__ == '__main__':
    print(json.dumps(validate_workflow({'steps':[{'run':'echo ok'}]}), ensure_ascii=False))
