import argparse
import json

from policies.shell_policy import ShellPolicy
from tools.terminal_tool import TerminalTool
from workflow_engine.workflow_graph import build_graph
from workflow_engine.workflow_parser import parse_workflow
from workflow_engine.workflow_validator import validate_workflow


def execute_workflow(workflow: dict) -> dict:
    check = validate_workflow(workflow)
    if not check['valid']:
        return {'status': 'blocked', 'issues': check['issues']}

    tool = TerminalTool(policy_engine=ShellPolicy(), log_dir='/home/adem/graywolf/logs')
    results = []
    for step in workflow.get('steps', []):
        cmd = step.get('run', '')
        results.append(tool.run_command(cmd))

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
