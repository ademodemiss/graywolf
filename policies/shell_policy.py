import os
import re
from enum import Enum


class PolicyDecision(str, Enum):
    ALLOW = "ALLOW"
    CONFIRM = "CONFIRM"
    DENY = "DENY"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ShellPolicy:
    def __init__(
        self,
        allowed_commands: list[str] | None = None,
        risky_commands: list[str] | None = None,
        forbidden_commands: list[str] | None = None,
    ):
        self.allowed_commands = allowed_commands if allowed_commands is not None else [
            "ls",
            "cat",
            "echo",
            "pwd",
            "grep",
            "find",
            "python",
            "python3",
            "pip",
            "git",
            "sed",
            "mkdir",
            "touch",
            "tee",
        ]
        self.risky_commands = risky_commands if risky_commands is not None else [
            "mv",
            "cp",
            "dd",
            "chmod",
            "chown",
            "apt",
            "apt-get",
            "npm",
            "node",
            "curl",
            "wget",
            "scp",
            "ssh",
        ]
        self.forbidden_commands = forbidden_commands if forbidden_commands is not None else [
            "sudo",
            "reboot",
            "shutdown",
            "poweroff",
            "init",
            "halt",
            "rm",
        ]
        self._dangerous_paths = ["/root", "/etc", "/sys", "/proc", "/dev", "/bin", "/sbin"]
        self._download_indicators = ["curl", "wget", "scp", "ssh", "nc", "perl"]
        self._chaining_tokens = ["&&", "||", ";", "|"]
        self._redirection_tokens = [">", ">>"]
        self._high_risk_patterns = [r"rm\s+-rf", r"dd\s+if=", r"chmod\s+\d{3}", r"mv\s+.*\s+/.+"]

    def evaluate(self, command: str) -> tuple[PolicyDecision, str]:
        normalized = (command or "").strip()
        if not normalized:
            return PolicyDecision.ALLOW, "Boş komut, erişim gerekmez."

        safe_tool_decision = self._evaluate_safe_tool_commands(normalized)
        if safe_tool_decision is not None:
            return safe_tool_decision

        safe_redirect_decision = self._evaluate_safe_redirection(normalized)
        if safe_redirect_decision is not None:
            return safe_redirect_decision

        cmd_parts = normalized.split()
        base_cmd = os.path.basename(cmd_parts[0]) if cmd_parts else ""

        if self._is_forbidden(base_cmd, normalized):
            return PolicyDecision.DENY, f"Komut '{base_cmd}' politika tarafından tamamen yasaklandı."

        if self._contains_chaining(normalized):
            return PolicyDecision.CONFIRM, "Zincirli komutlar çalıştırma önce onay gerektirir."

        if self._contains_redirection(normalized):
            return PolicyDecision.CONFIRM, "Yönlendirme içeriyor; önce onay alın."

        if self._contains_dangerous_path(normalized):
            return PolicyDecision.CONFIRM, "Sistem dosyalarını etkileyebilecek bir yol içeriyor."

        if self._contains_high_risk_pattern(normalized):
            return PolicyDecision.CONFIRM, "Yüksek riskli pattern algılandı; onay gerekli."

        if base_cmd in self.risky_commands or self._contains_download_behavior(normalized):
            return PolicyDecision.CONFIRM, f"'{base_cmd}' veya bağlantılı komut riskli olarak sınıflandırıldı."

        if base_cmd in self.allowed_commands:
            return PolicyDecision.ALLOW, f"Komut '{base_cmd}' politika tarafından izinli listededir."

        return PolicyDecision.CONFIRM, f"Komut '{base_cmd}' özel olarak tanımlı değil; onay gerekli."

    def _is_forbidden(self, base_cmd: str, command: str) -> bool:
        lowered = command.lower()
        if base_cmd in self.forbidden_commands:
            return True
        if "sudo" in lowered or "rm -rf" in lowered:
            return True
        return False

    def _contains_chaining(self, command: str) -> bool:
        return any(token in command for token in self._chaining_tokens)

    def _contains_redirection(self, command: str) -> bool:
        return any(token in command for token in self._redirection_tokens)

    def _contains_dangerous_path(self, command: str) -> bool:
        lowered = command.lower()
        return any(path in lowered and path != "/tmp" for path in self._dangerous_paths)

    def _contains_download_behavior(self, command: str) -> bool:
        lowered = command.lower()
        return any(tool in lowered for tool in self._download_indicators)

    def _contains_high_risk_pattern(self, command: str) -> bool:
        for pattern in self._high_risk_patterns:
            if re.search(pattern, command):
                return True
        return False

    def _evaluate_safe_tool_commands(self, command: str) -> tuple[PolicyDecision, str] | None:
        normalized = command.strip()
        if not normalized.startswith("file_tool.write("):
            return None

        path_match = re.search(r"path\s*=\s*['\"]([^'\"]+)['\"]", normalized)
        if not path_match:
            return PolicyDecision.CONFIRM, "file_tool.write path çözümlenemedi; onay gerekli."

        target = path_match.group(1)
        if self._is_safe_output_target(target):
            return PolicyDecision.ALLOW, "Güvenli file_tool.write hedefi (logs/reports/tasks) otomatik izinli."

        return PolicyDecision.CONFIRM, "file_tool.write hedefi güvenli izin listesinde değil; onay gerekli."

    def _evaluate_safe_redirection(self, command: str) -> tuple[PolicyDecision, str] | None:
        normalized = command.strip()
        redirect_match = re.search(r"(?:>|>>)\s*([^\s]+)\s*$", normalized)
        if not redirect_match:
            return None

        target = redirect_match.group(1).strip().strip("'\"")
        if self._is_safe_output_target(target):
            return PolicyDecision.ALLOW, "Güvenli çıktı yönlendirmesi (logs/reports/tasks) otomatik izinli."
        return None

    def _is_safe_output_target(self, target: str) -> bool:
        allowed_prefixes = [
            "/home/adem/graywolf/logs/",
            "/home/adem/graywolf/reports/",
            "/home/adem/graywolf/tasks/",
            "logs/",
            "reports/",
            "tasks/",
        ]
        return any(target.startswith(prefix) for prefix in allowed_prefixes)


if __name__ == "__main__":
    policy = ShellPolicy()
    tests = [
        "ls -l",
        "rm -rf /tmp/test",
        "sudo apt update",
        "echo a && echo b",
        "python my_script.py",
        "curl http://example",
        "deploy && reboot",
    ]
    for test in tests:
        decision, reason = policy.evaluate(test)
        print(test, decision, reason)
