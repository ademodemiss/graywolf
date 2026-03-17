"""DEPRECATED compatibility executor.
Use canonical workflow runner: workflows/runner.py::run_workflow
"""

import argparse
import json

from core.human_gate import HumanGate
from monitor.approval_notifier import ApprovalNotifier
from workflow_engine.workflow_graph import build_graph

ApprovalNotifier()
from workflow_engine.workflow_parser import parse_workflow
from workflow_engine.workflow_validator import validate_workflow


def execute_workflow(workflow: dict) -> dict:
    check = validate_workflow(workflow)
    if not check['valid']:
        return {'status': 'blocked', 'issues': check['issues']}

    gate = HumanGate()
    results = []
    for step in workflow.get('steps', []):
        cmd = step.get('run', '')
        step_name = step.get('name')
        results.append(gate.execute_command(cmd, step_name=step_name))

    return {'status': 'completed', 'graph': build_graph(workflow), 'results': results}


def main():
    p = argparse.ArgumentParser(description='GrayWolf Workflow Engine Executor')
    p.add_argument('--test', action='store_true')
    args = p.parse_args()

    if args.test:
        wf = parse_workflow({'steps': [{'run': 'echo wf-step-1'}, {'run': 'echo wf-step-2'}]})
        print(json.dumps(execute_workflow(wf), ensure_ascii=False))
        return

    print(json.dumps({'status': 'idle'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
