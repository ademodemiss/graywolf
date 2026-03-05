import os
from enum import Enum

class PolicyDecision(str, Enum):
    ALLOW = "ALLOW"
    CONFIRM = "CONFIRM"
    DENY = "DENY"

class ShellPolicy:
    def __init__(self, allowed_commands=None, risky_commands=None, forbidden_commands=None):
        self.allowed_commands = allowed_commands if allowed_commands is not None else ["ls", "cat", "echo", "pwd", "grep", "find", "python", "python3", "pip", "git", "sed", "mkdir", "touch", "tee"]
        self.risky_commands = risky_commands if risky_commands is not None else ["mv", "cp", "dd", "chmod", "chown", "apt", "apt-get", "npm", "node"]
        self.forbidden_commands = forbidden_commands if forbidden_commands is not None else ["sudo", "reboot", "shutdown", "poweroff", "init", "halt", "rm"]

    def evaluate(self, command: str) -> tuple[PolicyDecision, str]:
        cmd_parts = command.split(' ', 1)
        base_cmd = cmd_parts[0]
        base_name = os.path.basename(base_cmd)

        if base_name in self.forbidden_commands:
            return PolicyDecision.DENY, f"Command '{base_name}' is forbidden by policy."
        
        # Zincirli komut kontrolü
        if '&&' in command or '||' in command or ';' in command or '|' in command:
            return PolicyDecision.CONFIRM, "Chained commands require confirmation."

        if base_name in self.risky_commands:
            return PolicyDecision.CONFIRM, f"Command '{base_name}' is a risky command and requires confirmation."

        if base_name in self.allowed_commands:
            return PolicyDecision.ALLOW, f"Command '{base_name}' is allowed by policy."

        return PolicyDecision.CONFIRM, f"Command '{base_name}' is not explicitly allowed or denied; requires confirmation."

if __name__ == "__main__":
    policy = ShellPolicy()

    # Test cases
    print(policy.evaluate("ls -l"))
    print(policy.evaluate("rm -rf /"))
    print(policy.evaluate("sudo apt update"))
    print(policy.evaluate("echo a && echo b"))
    print(policy.evaluate("python my_script.py"))
    print(policy.evaluate("my_custom_command"))
