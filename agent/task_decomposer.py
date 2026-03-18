"""Agent task decomposer (aktif, minimal/no-break).

Parser çıktısını runtime command bus için çalıştırılabilir task intentine dönüştürür.
"""
from __future__ import annotations

from agent.command_parser import parse_command


def decompose_plan(command: str) -> list[dict]:
    parsed = parse_command(command)
    return [
        {
            "id": "step-1",
            "intent": parsed["intent"],
            "source": "agent-decomposer",
            "payload": {
                "goal": parsed["objective"],
                "text": parsed["objective"],
            },
        }
    ]


def plan_summary_from_command(command: str) -> dict:
    parsed = parse_command(command)
    steps = decompose_plan(command)
    return {
        "plan": parsed,
        "decomposed_steps": steps,
    }
