from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IntentDecision(str, Enum):
    ALLOW = "ALLOW"
    CONFIRM = "CONFIRM"
    DENY = "DENY"


@dataclass
class IntentPolicyResult:
    decision: IntentDecision
    reason: str
    risk: str


class IntentPolicy:
    """Intent-level policy gate for command bus.

    Graywolf-first simple defaults:
    - safe operational intents -> ALLOW
    - sensitive intents -> CONFIRM
    - forbidden intents -> DENY
    """

    ALLOW_INTENTS = {
        "healthcheck",
        "risk_summary",
        "repo_status",
        "chat_command",
        "status",
    }

    CONFIRM_INTENTS = {
        "deploy",
        "delete_artifact",
        "financial_trade",
        "system_change",
        "shutdown_service",
    }

    DENY_INTENTS = {
        "system_reboot",
        "wipe_data",
        "disable_guardrails",
    }

    def evaluate(self, intent: str, payload: dict | None = None) -> IntentPolicyResult:
        i = (intent or "").strip().lower()
        payload = payload or {}

        if i in self.DENY_INTENTS:
            return IntentPolicyResult(IntentDecision.DENY, f"intent '{i}' policy tarafından yasaklandı", "high")

        if i in self.CONFIRM_INTENTS:
            return IntentPolicyResult(IntentDecision.CONFIRM, f"intent '{i}' onay gerektirir", "high")

        # payload risk hint can elevate unknown intents
        risk_hint = str(payload.get("risk") or "").lower()
        if i not in self.ALLOW_INTENTS:
            if risk_hint in {"high", "critical"}:
                return IntentPolicyResult(IntentDecision.CONFIRM, f"intent '{i}' tanımsız ve risk={risk_hint}; onay gerekli", "high")
            return IntentPolicyResult(IntentDecision.CONFIRM, f"intent '{i}' tanımsız; onay gerekli", "medium")

        return IntentPolicyResult(IntentDecision.ALLOW, f"intent '{i}' izinli", "low")
