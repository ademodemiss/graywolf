"""Single-agent loop (v1.1 minimal).

Execution motoruna dokunmadan, üstte planla-yürüt-değerlendir döngüsü sağlar.
"""
from __future__ import annotations

from typing import Callable


def build_plan(user_goal: str, max_steps: int = 5) -> list[str]:
    goal = (user_goal or "").strip()
    if not goal:
        raise ValueError("empty_goal")

    seeds = [
        f"İsteği netleştir ve kapsamı çıkar: {goal}",
        f"İlk çalışır çözüm iskeletini oluştur: {goal}",
        f"Çözümü adım adım uygula: {goal}",
        "Temel doğrulama/test çalıştır ve sorunları toparla",
        "Sonucu kısa özetle ve varsa açık kalanları listele",
    ]

    step_count = max(3, min(max_steps, 5))
    return seeds[:step_count]


def evaluate_step(step_result: dict) -> dict:
    status = (step_result or {}).get("status", "unknown")
    accepted = status in {"ok", "queued", "confirm_required"}
    return {
        "accepted": accepted,
        "status": status,
        "reason": "continue" if accepted else "stop_on_error",
    }


def run_agent_loop(
    user_goal: str,
    step_runner: Callable[[str, int, int], dict],
    max_steps: int = 5,
) -> dict:
    plan = build_plan(user_goal, max_steps=max_steps)
    trace: list[dict] = []

    for idx, step in enumerate(plan, start=1):
        out = step_runner(step, idx, len(plan))
        ev = evaluate_step(out)
        trace.append(
            {
                "index": idx,
                "step": step,
                "result": out,
                "evaluation": ev,
            }
        )
        if not ev["accepted"]:
            return {
                "status": "error",
                "goal": user_goal,
                "plan": plan,
                "trace": trace,
                "completed_steps": idx - 1,
            }

    return {
        "status": "ok",
        "goal": user_goal,
        "plan": plan,
        "trace": trace,
        "completed_steps": len(plan),
    }
