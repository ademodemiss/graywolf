import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.self_improve_tool import SelfImproveTool


REPLAN_LOG = Path("/home/adem/graywolf/logs/self_improve_replan.log")
SCHEDULER_LOG = Path("/home/adem/graywolf/logs/self_improve_scheduler.log")
LEARNING_LOG = Path("/home/adem/graywolf/logs/self_improve_learning.log")
PROCESSED_FLAG = "processed_by_phase265"
LEARNING_FLAG = "processed_by_phase266"

SUCCESS_KEYWORDS = {"success", "completed", "ok", "done"}
WARNING_KEYWORDS = {"warn", "warning", "partial", "soft", "alert"}
FAILURE_KEYWORDS = {"fail", "failed", "error", "denied", "reject", "timeout"}
CATEGORY_SCORES = {
    "success": 95,
    "warning": 65,
    "failure": 20,
    "unknown": 50,
}


def _read_json_lines(path: Path | str) -> list[dict]:
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


def _write_json_lines(entries: list[dict], path: Path | str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _append_scheduler_log(job: dict, path: Path | str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    log_entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "request_id": job.get("request_id"),
        "workflow": job.get("workflow"),
        "analysis_status": job.get("analysis_status"),
        "approval_status": job.get("approval", {}).get("status"),
        "scheduler_event": job.get("event"),
        "processed": True,
    }
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def _determine_learning_category(job: dict) -> str:
    summary = (job.get("analysis_summary") or "").lower()
    status = (job.get("analysis_status") or "").lower()

    for keyword in FAILURE_KEYWORDS:
        if keyword in summary or keyword in status:
            return "failure"
    for keyword in WARNING_KEYWORDS:
        if keyword in summary or keyword in status:
            return "warning"
    for keyword in SUCCESS_KEYWORDS:
        if keyword in summary or keyword in status:
            return "success"
    return "unknown"


def _learning_reliability_score(category: str) -> int:
    return CATEGORY_SCORES.get(category, CATEGORY_SCORES["unknown"])


def _append_learning_log(job: dict, entry: dict | None, path: Path | str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = (entry or {}).get("payload") or {}
    analysis = (entry or {}).get("analysis") or {}
    learning_feedback = job.get("learning_feedback") or job.get("analysis_summary") or analysis.get("summary") or analysis.get("details") or ""
    learning_status = job.get("learning_status") or "scheduled"
    feedback_category = job.get("learning_feedback_category") or _determine_learning_category(job)
    reliability = job.get("learning_reliability_score") or _learning_reliability_score(feedback_category)
    follow_up = (
        job.get("learning_follow_up_notes")
        or job.get("analysis_summary")
        or analysis.get("details")
        or job.get("analysis_status")
        or learning_status
    )
    log_entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "request_id": job.get("request_id"),
        "workflow": job.get("workflow"),
        "start_source": payload.get("workflow_name") or payload.get("workflow") or payload.get("workflow_source") or "bilinmeyen",
        "learning_status": learning_status,
        "learning_feedback": learning_feedback,
        "learning_feedback_category": feedback_category,
        "learning_reliability_score": reliability,
        "learning_follow_up_notes": follow_up,
        "approval_status": job.get("approval", {}).get("status"),
        "learning_event": job.get("event"),
        "learning_duration_ms": job.get("duration_ms"),
    }
    if entry:
        if entry.get(PROCESSED_FLAG):
            log_entry[PROCESSED_FLAG] = entry.get(PROCESSED_FLAG)
        if entry.get(LEARNING_FLAG):
            log_entry[LEARNING_FLAG] = entry.get(LEARNING_FLAG)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def _calculate_duration_ms(start_ts: str | None) -> int | None:
    if not start_ts:
        return None
    try:
        start = datetime.fromisoformat(start_ts)
        if not start.tzinfo:
            start = start.replace(tzinfo=timezone.utc)
        elapsed = datetime.now(timezone.utc) - start
        return int(elapsed.total_seconds() * 1000)
    except Exception:
        return None


def run_scheduler(
    log_path: Path | str = REPLAN_LOG,
    scheduler_log_path: Path | str = SCHEDULER_LOG,
    limit: int = 5,
) -> dict:
    entries = _read_json_lines(log_path)
    entry_lookup: dict[str, dict] = {}
    granted_unprocessed: list[dict] = []

    for entry in entries:
        approval = (entry.get("approval_request") or {})
        request_id = approval.get("request_id")
        if request_id:
            entry_lookup[request_id] = entry
        if approval.get("status") == "GRANTED" and request_id and not entry.get(PROCESSED_FLAG):
            granted_unprocessed.append(entry)

    pending_before = len(granted_unprocessed)
    jobs = SelfImproveTool.improve_from_replan_entries(granted_unprocessed, limit=limit)
    processed_ids = {job.get("request_id") for job in jobs if job.get("request_id")}
    processed = 0
    updated = False
    processed_ts = datetime.now(timezone.utc).isoformat()

    for entry in entries:
        request_id = (entry.get("approval_request") or {}).get("request_id")
        if request_id in processed_ids and not entry.get(PROCESSED_FLAG):
            entry[PROCESSED_FLAG] = {"ts": processed_ts, "scheduler": "phase265"}
            entry[LEARNING_FLAG] = {"ts": processed_ts, "scheduler": "phase266"}
            processed += 1
            updated = True

    if updated:
        _write_json_lines(entries, log_path)

    for job in jobs:
        job_result = SelfImproveTool.execute_pending_job(job)
        if job_result:
            job.update(job_result)
        entry = entry_lookup.get(job.get("request_id"))
        job["duration_ms"] = _calculate_duration_ms((entry or {}).get("ts"))
        _append_scheduler_log(job, scheduler_log_path)
        _append_learning_log(job, entry, LEARNING_LOG)

    return {
        "processed": processed,
        "pending_before": pending_before,
        "pending_after": max(pending_before - processed, 0),
        "jobs": len(jobs),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 265 replan scheduler")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--interval", type=int, default=60, help="Bekleme süresi (saniye)")
    parser.add_argument("--watch", action="store_true", help="Sürekli çalıştır")
    parser.add_argument("--log-path", default=str(REPLAN_LOG))
    parser.add_argument("--scheduler-log", default=str(SCHEDULER_LOG))
    args = parser.parse_args()

    if args.watch:
        while True:
            result = run_scheduler(args.log_path, args.scheduler_log, limit=args.limit)
            print(json.dumps(result, ensure_ascii=False))
            time.sleep(args.interval)
    else:
        result = run_scheduler(args.log_path, args.scheduler_log, limit=args.limit)
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
