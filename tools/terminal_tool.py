import argparse
import datetime
import json
import os
import shlex
import subprocess
import time

from policies.shell_policy import PolicyDecision, ShellPolicy


class TerminalTool:
    def __init__(self, policy_engine: ShellPolicy, log_dir: str = "/home/adem/graywolf/logs", work_dir: str = "/home/adem/graywolf"):
        self.policy_engine = policy_engine
        self.log_dir = os.path.expanduser(log_dir)
        self.work_dir = os.path.expanduser(work_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.work_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "terminal.log")

    def run_command(self, command: str, timeout: int = 60, policy_decision: PolicyDecision | None = None, policy_reason: str | None = None) -> dict:
        start_time = time.time()
        cwd = self.work_dir
        if policy_decision is None:
            decision, reason = self.policy_engine.evaluate(command)
        else:
            decision = policy_decision
            reason = policy_reason or ""

        log_entry = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "cwd": cwd,
            "cmd": command,
            "decision": decision.value,
            "reason": reason,
            "exit_code": None,
            "duration_ms": None,
            "stdout_len": 0,
            "stderr_len": 0,
        }

        def finalize(status: str, stdout: str = "", stderr: str = "", exit_code: int = 0) -> dict:
            log_entry["exit_code"] = exit_code
            log_entry["stdout_len"] = len(stdout or "")
            log_entry["stderr_len"] = len(stderr or "")
            log_entry["duration_ms"] = int((time.time() - start_time) * 1000)
            self._write_log(log_entry)
            return {
                "status": status,
                "stdout": (stdout or "").strip(),
                "stderr": (stderr or "").strip(),
                "log": log_entry,
            }

        if decision == PolicyDecision.DENY:
            return finalize("blocked", stderr="Command blocked by policy.", exit_code=1)

        if decision == PolicyDecision.CONFIRM:
            return finalize("needs_confirmation", stderr="Command requires confirmation.", exit_code=2)

        try:
            use_shell = any(token in command for token in [">", ">>"])
            process = subprocess.run(
                command if use_shell else shlex.split(command),
                capture_output=True,
                text=True,
                check=False,
                shell=use_shell,
                timeout=timeout,
                cwd=self.work_dir,
            )
            status = "success" if process.returncode == 0 else "error"
            return finalize(status, process.stdout, process.stderr, process.returncode)
        except FileNotFoundError:
            base = shlex.split(command)[0] if command.strip() else ""
            return finalize("error", stderr=f"Command '{base}' not found.", exit_code=127)
        except subprocess.TimeoutExpired as e:
            return finalize("timeout", (e.stdout or ""), "Command timed out.", 124)
        except Exception as e:
            return finalize("error", stderr=str(e), exit_code=1)

    def _write_log(self, entry: dict):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GrayWolf TerminalTool")
    parser.add_argument("--cmd", help="Command to execute")
    parser.add_argument("--timeout", type=int, default=60)
    return parser


if __name__ == "__main__":
    parser = _build_cli()
    args = parser.parse_args()

    tool = TerminalTool(policy_engine=ShellPolicy(), log_dir="/home/adem/graywolf/logs")

    if args.cmd:
        result = tool.run_command(args.cmd, timeout=args.timeout)
        print(json.dumps(result, ensure_ascii=False))
    else:
        print("Usage: python -m tools.terminal_tool --cmd \"<command>\"")
