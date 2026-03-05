import json

from policies.shell_policy import ShellPolicy
from tools.terminal_tool import TerminalTool


def run_smoke() -> dict:
    tool = TerminalTool(policy_engine=ShellPolicy(), log_dir="/home/adem/graywolf/logs")
    checks = [
        ("python_ok", "python3 -c \"print('ok')\""),
        ("policy_confirm", "echo a && echo b"),
        ("policy_deny", "rm -rf /"),
    ]

    results = []
    for name, cmd in checks:
        result = tool.run_command(cmd)
        results.append(
            {
                "name": name,
                "cmd": cmd,
                "status": result.get("status"),
                "decision": result.get("log", {}).get("decision"),
                "exit_code": result.get("log", {}).get("exit_code"),
            }
        )

    return {"status": "completed", "results": results}


if __name__ == "__main__":
    print(json.dumps(run_smoke(), ensure_ascii=False))
