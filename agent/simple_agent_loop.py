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


def _alternative_step(failed_step: str, failure_class: str) -> str:
    if failure_class == "blocked":
        return f"Alternatif yaklaşım: bağımlılık/izin önkontrolü yapıp tekrar dene ({failed_step})"
    return f"Alternatif yaklaşım: farklı sırada/alt parçalarla uygula ({failed_step})"


def _strategy_order(failure_class: str, safe_to_skip: bool) -> list[str]:
    if failure_class == "timeout":
        return ["skip_step" if safe_to_skip else "fallback_step"]
    if failure_class == "blocked":
        return ["alternative_step", "fallback_step"]
    # failed / unknown
    return ["alternative_step", "skip_step" if safe_to_skip else "fallback_step"]


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


def _final_state_label(classification: str) -> str:
    if classification == "completed":
        return "tamamlandı"
    if classification == "partially_completed":
        return "kısmen tamamlandı"
    return "yarım kaldı"


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
        original_step = plan[idx - 1]
        step = original_step
        attempts = 0
        out: dict = {}
        ev: dict = {"accepted": False, "status": "unknown", "reason": "not_started"}

        def _execute(candidate_step: str) -> tuple[dict, dict, int]:
            local_attempts = 0
            local_out: dict = {}
            local_ev: dict = {"accepted": False, "status": "unknown", "reason": "not_started"}
            while local_attempts <= max(0, timeout_retries):
                local_attempts += 1
                local_out = step_runner(candidate_step, idx, len(plan))
                local_ev = evaluate_step(local_out)
                if local_ev["accepted"]:
                    break
                if local_ev["reason"] == "timeout" and local_attempts <= max(0, timeout_retries):
                    continue
                break
            return local_out, local_ev, local_attempts

        out, ev, attempts = _execute(step)

        classification = classify_failure(out)
        recovery_attempt = 0
        recovery_strategy = None
        alternatives_tried: list[str] = []
        replan_depth = 0
        fallback_used = False
        replanned = False

        if not ev["accepted"] and ev["reason"] not in {"approval_required"}:
            safe_to_skip = _is_step_safe_to_skip(step)
            strategies = _strategy_order(classification, safe_to_skip)

            for strategy in strategies[:2]:  # recovery limit: 2
                recovery_attempt += 1
                recovery_strategy = strategy

                if strategy == "skip_step":
                    break

                if strategy == "alternative_step" and classification in {"failed", "blocked"} and replan_depth < 1:
                    alt = _alternative_step(original_step, classification)
                    alternatives_tried.append("alternative_step")
                    plan[idx - 1] = alt
                    step = alt
                    replan_depth = 1
                    replanned = True
                    out, ev, attempts = _execute(step)
                    classification = classify_failure(out)
                    if ev["accepted"]:
                        break
                    continue

                if strategy == "fallback_step" and replan_depth < 1:
                    fb = _fallback_step(original_step)
                    alternatives_tried.append("fallback_step")
                    plan[idx - 1] = fb
                    step = fb
                    replan_depth = 1
                    fallback_used = True
                    replanned = True
                    out, ev, attempts = _execute(step)
                    classification = classify_failure(out)
                    if ev["accepted"]:
                        break
                    continue

        step_summary = (out or {}).get("summary", "")
        if ev.get("reason") == "timeout" and attempts > max(0, timeout_retries):
            step_summary = f"{step_summary} Retry limiti aşıldı ({timeout_retries}).".strip()

        final_reason = "completed" if ev.get("accepted") else f"stopped:{ev.get('reason', 'unknown')}"
        if not ev.get("accepted") and recovery_attempt >= 2:
            final_reason = "recovery_limit_reached"

        trace.append(
            {
                "index": idx,
                "step": step,
                "original_step": original_step,
                "attempts": attempts,
                "result": out,
                "summary": step_summary,
                "evaluation": ev,
                "recovery_attempt": recovery_attempt,
                "recovery_strategy": recovery_strategy,
                "alternatives_tried": alternatives_tried,
                "replan_depth": replan_depth,
                "fallback_used": fallback_used,
                "replanned": replanned,
                "failure_classification": classification,
                "final_reason": final_reason,
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
                        "classification": "blocked",
                        "reason": f"Adım {idx} onay bekliyor.",
                    },
                }

            if recovery_strategy == "skip_step":
                idx += 1
                continue

            completed_so_far = len([t for t in trace if (t.get("evaluation") or {}).get("accepted")])
            majority_done = completed_so_far >= max(1, len(plan) - 1)
            completion_step_tried = False
            completion_success = False

            if majority_done:
                completion_step_tried = True
                completion_step = f"Güvenli completion adımı: çıktıyı doğrula ve güvenli kapanış özeti üret ({user_goal})"
                c_out, c_ev, c_attempts = _execute(completion_step)
                completion_success = bool((c_ev or {}).get("accepted"))
                trace.append(
                    {
                        "index": idx,
                        "step": completion_step,
                        "original_step": completion_step,
                        "attempts": c_attempts,
                        "result": c_out,
                        "summary": (c_out or {}).get("summary", ""),
                        "evaluation": c_ev,
                        "recovery_attempt": 1,
                        "recovery_strategy": "completion_step",
                        "alternatives_tried": ["completion_step"],
                        "replan_depth": 0,
                        "fallback_used": False,
                        "replanned": False,
                        "failure_classification": classify_failure(c_out),
                        "final_reason": "completion_step_success" if completion_success else "completion_step_failed",
                    }
                )

            if completion_success:
                return {
                    "status": "ok",
                    "goal": user_goal,
                    "plan": plan,
                    "trace": trace,
                    "completed_steps": len([t for t in trace if (t.get("evaluation") or {}).get("accepted")]),
                    "final": {
                        "state": _final_state_label("partially_completed"),
                        "classification": "partially_completed",
                        "reason": f"Adım {idx} başarısız olsa da güvenli completion adımıyla run kapatıldı.",
                    },
                }

            final_class = "blocked" if classification == "blocked" else "failed"
            reason_tail = "completion denemesi başarısız." if completion_step_tried else "completion denemesi uygulanmadı."
            return {
                "status": "error",
                "goal": user_goal,
                "plan": plan,
                "trace": trace,
                "completed_steps": idx - 1,
                "final": {
                    "state": _final_state_label(final_class),
                    "classification": final_class,
                    "reason": f"Adım {idx} başarısız oldu: {(out or {}).get('status', 'unknown')} ({reason_tail})",
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
            "state": _final_state_label("completed"),
            "classification": "completed",
            "reason": f"{len(trace)} adım işlendi; recovery/replan varsa trace üzerinde işlendi.",
        },
    }
