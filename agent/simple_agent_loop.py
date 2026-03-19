"""Single-agent loop (v1.1 minimal).

Execution motoruna dokunmadan, üstte planla-yürüt-değerlendir döngüsü sağlar.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
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


def wait_for_task_completion(task_id: str, processed_dir: str, timeout_seconds: int = 45) -> dict:
    """Processed task sonucunu bekle (gerçek task dosyası üzerinden)."""
    path = Path(processed_dir) / f"{task_id}.json"
    deadline = time.time() + max(1, timeout_seconds)

    while time.time() < deadline:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception as e:
                return {"status": "error", "summary": f"Task sonucu okunamadı: {e}"}

            raw = (data or {}).get("status", "unknown")
            if raw == "completed":
                return {"status": "completed", "summary": f"Task {task_id} tamamlandı."}
            if raw in {"failed", "error", "blocked"}:
                return {"status": "failed", "summary": f"Task {task_id} başarısız: {raw}", "raw_status": raw}
            return {"status": raw, "summary": f"Task {task_id} işlendi: {raw}"}
        time.sleep(1.0)

    return {"status": "timeout", "summary": f"Task {task_id} sonucu {timeout_seconds}s içinde tamamlanmadı."}


def evaluate_step(step_result: dict) -> dict:
    status = (step_result or {}).get("status", "unknown")

    if status == "completed":
        return {"accepted": True, "status": status, "reason": "continue"}

    if status == "confirm_required":
        return {"accepted": False, "status": status, "reason": "approval_required"}

    if status == "timeout":
        return {"accepted": False, "status": status, "reason": "timeout"}

    return {"accepted": False, "status": status, "reason": "stop_on_error"}


def run_agent_loop(
    user_goal: str,
    step_runner: Callable[[str, int, int], dict],
    max_steps: int = 5,
    timeout_retries: int = 1,
) -> dict:
    plan = build_plan(user_goal, max_steps=max_steps)
    trace: list[dict] = []

    for idx, step in enumerate(plan, start=1):
        attempts = 0
        out: dict = {}
        ev: dict = {"accepted": False, "status": "unknown", "reason": "not_started"}

        while attempts <= max(0, timeout_retries):
            attempts += 1
            out = step_runner(step, idx, len(plan))
            ev = evaluate_step(out)

            if ev["accepted"]:
                break

            if ev["reason"] == "timeout" and attempts <= max(0, timeout_retries):
                continue

            break

        step_summary = (out or {}).get("summary", "")
        if ev.get("reason") == "timeout" and attempts > max(0, timeout_retries):
            step_summary = f"{step_summary} Retry limiti aşıldı ({timeout_retries}).".strip()

        trace.append(
            {
                "index": idx,
                "step": step,
                "attempts": attempts,
                "result": out,
                "summary": step_summary,
                "evaluation": ev,
            }
        )

        if not ev["accepted"]:
            if ev["reason"] == "approval_required":
                return {
                    "status": "confirm_required",
                    "goal": user_goal,
                    "plan": plan,
                    "trace": trace,
                    "completed_steps": idx - 1,
                    "final": {
                        "state": "yarım kaldı",
                        "reason": f"Adım {idx} onay bekliyor.",
                    },
                }

            if ev["reason"] == "timeout":
                return {
                    "status": "error",
                    "goal": user_goal,
                    "plan": plan,
                    "trace": trace,
                    "completed_steps": idx - 1,
                    "final": {
                        "state": "yarım kaldı",
                        "reason": f"Adım {idx} timeout oldu, retry sonrası da tamamlanamadı.",
                    },
                }

            return {
                "status": "error",
                "goal": user_goal,
                "plan": plan,
                "trace": trace,
                "completed_steps": idx - 1,
                "final": {
                    "state": "yarım kaldı",
                    "reason": f"Adım {idx} başarısız oldu: {(out or {}).get('status', 'unknown')}",
                },
            }

    return {
        "status": "ok",
        "goal": user_goal,
        "plan": plan,
        "trace": trace,
        "completed_steps": len(plan),
        "final": {
            "state": "tamamlandı",
            "reason": f"{len(plan)} adım başarıyla tamamlandı.",
        },
    }
