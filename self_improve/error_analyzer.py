import re
from typing import Dict, Any


class ErrorAnalyzer:
    _REPLAN_HINTS: Dict[str, str] = {
        "syntax_error": "fix_syntax_and_retry",
        "dependency_error": "verify_dependencies",
        "timeout": "retry_with_backoff",
        "command_or_file_not_found": "check_paths",
        "permission_error": "elevate_permissions",
        "auth_error": "refresh_credentials",
        "rate_limit_error": "slow_down",
        "network_error": "check_connectivity",
        "unknown_error": "retry_general",
    }

    def analyze(self, error: str, task_context: Dict) -> Dict[str, Any]:
        error = str(error).lower()
        analysis = {
            "error_type": "unknown",
            "severity": "medium",
            "suggested_action": "retry",
            "confidence": 0.5
        }
        if "syntaxerror" in error or "indentationerror" in error:
            analysis.update({"error_type": "syntax_error", "severity": "high", "suggested_action": "fix_syntax", "confidence": 0.9})
        elif "modulenotfound" in error or "importerror" in error:
            analysis.update({"error_type": "dependency_error", "severity": "medium", "suggested_action": "install_dependency", "confidence": 0.8})
        elif "timeout" in error:
            analysis.update({"error_type": "timeout", "severity": "low", "suggested_action": "retry_with_backoff", "confidence": 0.9})
        return analysis

    def classify_failure(self, stderr: str) -> Dict[str, str]:
        if stderr is None:
            stderr = ""
        cleaned = stderr.lower()
        category = "unknown_error"
        if "command not found" in cleaned or "no such file or directory" in cleaned:
            category = "command_or_file_not_found"
        elif "permission denied" in cleaned or "access denied" in cleaned:
            category = "permission_error"
        elif "api key" in cleaned or "auth" in cleaned or "token" in cleaned or "authentication" in cleaned:
            category = "auth_error"
        elif "rate limit" in cleaned or "429" in cleaned or "quota" in cleaned:
            category = "rate_limit_error"
        elif "timeout" in cleaned or "timed out" in cleaned:
            category = "timeout"
        elif "network" in cleaned or "connection" in cleaned or "dns" in cleaned:
            category = "network_error"

        hint = self._REPLAN_HINTS.get(category, self._REPLAN_HINTS["unknown_error"])
        return {"category": category, "replan_hint": hint}

    def replan_hint_for_category(self, category: str) -> str:
        return self._REPLAN_HINTS.get(category, self._REPLAN_HINTS["unknown_error"])
