import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from monitor.replan_learning_reporter import (
    DEFAULT_WINDOW_HOURS,
    RELIABILITY_THRESHOLD,
    _read_log_entries,
    build_learning_stats,
)
from monitor.replan_self_improve_scheduler import REPLAN_LOG, SCHEDULER_LOG, run_scheduler
from monitor.telegram_alert import send_telegram_message

LEARNING_LOG = Path("/home/adem/graywolf/logs/self_improve_learning.log")
RECOVERY_LOG = Path("/home/adem/graywolf/logs/learning_recovery.log")
SUGGESTIONS_PATH = Path("/home/adem/graywolf/logs/learning_recovery_suggestions.json")
RETRY_EVENT = "learning_autopilot_retry"


def _parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _load_recovery_entries(path: Path | str = RECOVERY_LOG) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    entries: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def _parse_scheduler_result(result: dict) -> dict:
    return {
        "processed": result.get("processed"),
        "jobs": result.get("jobs"),
        "pending_before": result.get("pending_before"),
    }


def _should_retry(stats: dict) -> Literal["low_reliability", "failure_spike", "no"]:
    reliability = stats.get("reliability_score")
    failure_count = stats.get("failure_count", 0)
    if reliability is not None and reliability < RELIABILITY_THRESHOLD:
        return "low_reliability"
    if failure_count >= 3:
        return "failure_spike"
    return "no"


def _already_retried(latest_request: str | None, history: list[dict]) -> bool:
    if not latest_request:
        return False
    for entry in history:
        if entry.get("new_request_id") == latest_request:
            return True
    return False


def _append_replan_entry(entry: dict, path: Path | str = REPLAN_LOG) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _append_recovery_log(entry: dict, path: Path | str = RECOVERY_LOG) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _update_suggestions_section(section: str, payload: dict, path: Path | str = SUGGESTIONS_PATH) -> None:
    p = Path(path)
    data: dict = {}
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8")) or {}
        except Exception:
            data = {}
    data[section] = payload
    data["ts"] = datetime.now(timezone.utc).isoformat()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _build_replan_entry(latest_entry: dict, new_request_id: str, reason: str) -> dict:
    payload = {
        "workflow": latest_entry.get("workflow"),
        "workflow_name": latest_entry.get("workflow"),
        "workflow_source": latest_entry.get("start_source"),
        "learning_retry_reason": reason,
    }
    analysis = {
        "summary": latest_entry.get("learning_feedback"),
        "status": latest_entry.get("learning_status"),
        "details": latest_entry.get("learning_follow_up_notes"),
    }
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": RETRY_EVENT,
        "payload": payload,
        "analysis": analysis,
        "approval_request": {
            "request_id": new_request_id,
            "status": "GRANTED",
            "granted_at": datetime.now(timezone.utc).isoformat(),
            "granted_by": "learning_autopilot",
        },
        "metadata": {
            "autopilot_retry": True,
            "original_request_id": latest_entry.get("request_id"),
            "reason": reason,
        },
    }


def _format_reason(reason: str) -> str:
    if reason == "low_reliability":
        return "reliability score < %s" % RELIABILITY_THRESHOLD
    if reason == "failure_spike":
        return "failure count ≥ 3"
    return ""


def _build_autopilot_summary(latest_entry: dict, stats: dict, reason_text: str, scheduler_result: dict) -> dict:
    workflow = latest_entry.get("workflow") or "bilinmeyen"
    reliability_score = stats.get("reliability_score")
    reliability_display = f"{reliability_score:.1f}%" if reliability_score is not None else "N/A"
    failure_count = stats.get("failure_count", 0)
    pending_count = stats.get("pending", 0)
    summary = (
        f"Autopilot yeniden çalıştı: {workflow} ({latest_entry.get('request_id')}) ↻ "
        f"reason {reason_text} | reliability {reliability_display}, "
        f"failures={failure_count} | pending={pending_count}"
    )
    return {
        "summary": summary,
        "workflow": workflow,
        "original_request_id": latest_entry.get("request_id"),
        "reliability_score": reliability_score,
        "failure_count": failure_count,
        "pending": pending_count,
        "scheduler": scheduler_result,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 268 learning autopilot")
    parser.add_argument("--log", default=str(LEARNING_LOG))
    parser.add_argument("--window-hours", type=int, default=DEFAULT_WINDOW_HOURS)
    parser.add_argument("--replan-log", default=str(REPLAN_LOG))
    parser.add_argument("--scheduler-log", default=str(SCHEDULER_LOG))
    parser.add_argument("--recovery-log", default=str(RECOVERY_LOG))
    parser.add_argument("--suggestions", default=str(SUGGESTIONS_PATH))
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    entries = _read_log_entries(args.log)
    if not entries:
        print("Öğrenme geçmişi yok.")
        return

    history = _load_recovery_entries(args.recovery_log)
    stats = build_learning_stats(entries, args.window_hours)
    reason_key = _should_retry(stats)
    if reason_key == "no":
        print("Autopilot koşulları oluşmadı.")
        return

    latest_entry = entries[-1]
    latest_request_id = latest_entry.get("request_id")
    if _already_retried(latest_request_id, history):
        print("Son job için zaten autopilot yeniden denemesi yapıldı.")
        return

    reason_text = _format_reason(reason_key)
    new_request_id = f"{latest_request_id}-auto-{uuid.uuid4().hex[:6]}"
    replan_entry = _build_replan_entry(latest_entry, new_request_id, reason_key)

    scheduler_result = {}
    if not args.dry_run:
        _append_replan_entry(replan_entry, args.replan_log)
        scheduler_result = run_scheduler(args.replan_log, args.scheduler_log, limit=1)

    recovery_record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": "auto_retry",
        "original_request_id": latest_request_id,
        "new_request_id": new_request_id,
        "reason": reason_text,
        "reliability_score": stats.get("reliability_score"),
        "failure_count": stats.get("failure_count"),
        "pending": stats.get("pending"),
        "scheduler": _parse_scheduler_result(scheduler_result),
    }
    if not args.dry_run:
        _append_recovery_log(recovery_record, args.recovery_log)
        autopilot_summary = _build_autopilot_summary(latest_entry, stats, reason_text, recovery_record["scheduler"])
        _update_suggestions_section("autopilot", autopilot_summary, args.suggestions)

    message = (
        f"Phase 268 Autopilot: {reason_text} → new job {new_request_id}"
        if reason_text
        else f"Phase 268 Autopilot: yeni job {new_request_id}"
    )
    print(message)
    if args.telegram and not args.dry_run:
        send_telegram_message(message)


if __name__ == "__main__":
    main()
