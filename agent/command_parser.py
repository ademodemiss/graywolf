"""Agent command parser (aktif, minimal/no-break).

Doğal dil komutu normalize eder ve decomposer/dispatcher için plan iskeleti üretir.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ParsedCommand:
    objective: str
    intent: str
    source: str = "agent-parser"


INTENT_KEYWORDS = {
    "deploy": ("deploy", "yayın", "production", "release"),
    "healthcheck": ("health", "sağlık", "precheck", "doktor"),
    "analyze": ("analiz", "analysis", "incele", "report"),
}


def infer_intent(command: str) -> str:
    lowered = (command or "").lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(k in lowered for k in keywords):
            return intent
    return "execute"


def parse_command(command: str, source: str = "agent-parser") -> dict:
    objective = (command or "").strip()
    if not objective:
        raise ValueError("empty_command")

    parsed = ParsedCommand(objective=objective, intent=infer_intent(objective), source=source)
    return {
        "objective": parsed.objective,
        "intent": parsed.intent,
        "source": parsed.source,
    }
