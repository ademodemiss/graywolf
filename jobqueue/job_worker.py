import json

from policies.shell_policy import ShellPolicy
from tools.terminal_tool import TerminalTool


def run_command(command: str) -> dict:
    tool = TerminalTool(policy_engine=ShellPolicy(), log_dir='/home/adem/graywolf/logs')
    return tool.run_command(command)


if __name__ == '__main__':
    print(json.dumps(run_command('echo worker-test'), ensure_ascii=False))
