"""Single-agent loop (v1.1 minimal).

Execution motoruna dokunmadan, üstte planla-yürüt-değerlendir döngüsü sağlar.
"""
from __future__ import annotations

import json
import time
from datetime import datetime
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


def classify_failure(step_result: dict) -> str:
    status = str((step_result or {}).get("status", "unknown")).lower()
    if status == "timeout":
        return "timeout"
    if status == "failed":
        return "failed"
    if status == "blocked":
        return "blocked"
    if status == "error":
        return "failed"
    return "unknown"


def evaluate_step(step_result: dict) -> dict:
    status = (step_result or {}).get("status", "unknown")

    if status == "completed":
        return {"accepted": True, "status": status, "reason": "continue"}
    if status == "confirm_required":
        return {"accepted": False, "status": status, "reason": "approval_required"}
    if status == "timeout":
        return {"accepted": False, "status": status, "reason": "timeout"}
    return {"accepted": False, "status": status, "reason": "stop_on_error"}


def _is_step_safe_to_skip(step: str) -> bool:
    lowered = (step or "").lower()
    risky = ("deploy", "production", "release", "delete", "drop", "migrate")
    return not any(k in lowered for k in risky)


def _fallback_step(failed_step: str) -> str:
    return f"Güvenli fallback: önce durum/log kontrolü yap ve ardından devam et ({failed_step})"


def save_agent_state(state_dir: str, run_id: str, state: dict) -> str:
    d = Path(state_dir)
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{run_id}.json"
    payload = {**state, "updated_at": datetime.now().isoformat()}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return str(path)


def load_agent_state(state_dir: str, run_id: str) -> dict | None:
    path = Path(state_dir) / f"{run_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def find_state_by_request_id(state_dir: str, request_id: str) -> dict | None:
    d = Path(state_dir)
    if not d.exists():
        return None
    for p in sorted(d.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        pause = (data or {}).get("pause") or {}
        if pause.get("approval_request_id") == request_id and (data or {}).get("status") == "confirm_required":
            return data
    return None


def run_agent_loop(
    user_goal: str,
    step_runner: Callable[[str, int, int], dict],
    max_steps: int = 5,
    timeout_retries: int = 1,
    start_index: int = 1,
    existing_plan: list[str] | None = None,
    existing_trace: list[dict] | None = None,
) -> dict:
    plan = list(existing_plan or build_plan(user_goal, max_steps=max_steps))
    trace: list[dict] = list(existing_trace or [])
    replans_used = 0
    idx = start_index

    while idx <= len(plan):
        step = plan[idx - 1]
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

        classification = classify_failure(out)
        step_summary = (out or {}).get("summary", "")
        if ev.get("reason") == "timeout" and attempts > max(0, timeout_retries):
            step_summary = f"{step_summary} Retry limiti aşıldı ({timeout_retries}).".strip()

        recovery_attempt = None
        fallback_used = False
        replanned = False

        if not ev["accepted"] and ev["reason"] not in {"approval_required"}:
            safe_to_skip = _is_step_safe_to_skip(step)
            if safe_to_skip:
                recovery_attempt = "skip_step"
            elif replans_used < 1:
                fallback = _fallback_step(step)
                plan.insert(idx, fallback)
                replans_used += 1
                recovery_attempt = "insert_fallback"
                fallback_used = True
                replanned = True
            else:
                recovery_attempt = "stop"

        trace.append(
            {
                "index": idx,
                "step": step,
                "attempts": attempts,
                "result": out,
                "summary": step_summary,
                "evaluation": ev,
                "recovery_attempt": recovery_attempt,
                "fallback_used": fallback_used,
                "replanned": replanned,
                "failure_classification": classification,
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
                    "pause": {
                        "step_index": idx,
                        "approval_request_id": (out or {}).get("approval_request_id"),
                    },
                    "final": {
                        "state": "yarım kaldı",
                        "reason": f"Adım {idx} onay bekliyor.",
                    },
                }

            if recovery_attempt == "skip_step":
                idx += 1
                continue

            if recovery_attempt == "insert_fallback":
                idx += 1
                continue

            if ev["reason"] == "timeout":
                return {
                    "status": "error",
                    "goal": user_goal,
                    "plan": plan,
                    "trace": trace,
                    "completed_steps": idx - 1,
                    "final": {
                        "state": "yarım kaldı",
                        "reason": f"Adım {idx} timeout oldu, recovery sonrası da tamamlanamadı.",
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

        idx += 1

    return {
        "status": "ok",
        "goal": user_goal,
        "plan": plan,
        "trace": trace,
        "completed_steps": len([t for t in trace if (t.get('evaluation') or {}).get('accepted')]),
        "final": {
            "state": "tamamlandı",
            "reason": f"{len(trace)} adım işlendi; recovery/replan varsa trace üzerinde işlendi.",
        },
    }
