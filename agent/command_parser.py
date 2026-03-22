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
    confidence: float = 0.0
    fallback: bool = False
    hint: str = ""


INTENT_KEYWORDS = {
    "deploy": ("deploy", "yayın", "production", "release"),
    "healthcheck": ("health", "sağlık", "precheck", "doktor"),
    "analyze": ("analiz", "analysis", "incele", "report"),
}

LOW_RISK_SCRIPT_PATTERNS = (
    "script yaz",
    "python script yaz",
    "basit script oluştur",
    "script oluştur",
)

HIGH_RISK_GUARD_PATTERNS = (
    "deploy",
    "production",
    "release",
    "migrate",
    "delete",
    "drop",
)


def infer_intent_with_confidence(command: str) -> tuple[str, float]:
    lowered = (command or "").lower()

    # Dar intent tuning:
    # Düşük risk script üretim istekleri gereksiz execute->confirm zincirine düşmesin.
    # High-risk çağrışım varsa bu kural devreye girmez.
    # chat_command policy'de ALLOW olduğundan burada en güvenli dar eşleme olarak kullanılır.
    if any(p in lowered for p in LOW_RISK_SCRIPT_PATTERNS) and not any(h in lowered for h in HIGH_RISK_GUARD_PATTERNS):
        return "chat_command", 0.72

    scores: dict[str, float] = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        matches = sum(1 for k in keywords if k in lowered)
        if matches:
            scores[intent] = matches / max(len(keywords), 1)

    if not scores:
        return "execute", 0.20

    best_intent, best_score = max(scores.items(), key=lambda kv: kv[1])
    return best_intent, float(best_score)


def parse_command(command: str, source: str = "agent-parser") -> dict:
    objective = (command or "").strip()
    if not objective:
        raise ValueError("empty_command")

    intent, confidence = infer_intent_with_confidence(objective)
    fallback = intent == "execute" and confidence <= 0.25
    hint = ""
    if fallback:
        hint = "Niyet net değil; güvenli fallback intent=execute seçildi."

    parsed = ParsedCommand(
        objective=objective,
        intent=intent,
        source=source,
        confidence=confidence,
        fallback=fallback,
        hint=hint,
    )
    return {
        "objective": parsed.objective,
        "intent": parsed.intent,
        "source": parsed.source,
        "confidence": round(parsed.confidence, 2),
        "fallback": parsed.fallback,
        "hint": parsed.hint,
    }
