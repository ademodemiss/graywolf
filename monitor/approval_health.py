import argparse
import ast
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


REPLAN_LOG = "/home/adem/graywolf/logs/self_improve_replan.log"
APPROVAL_LOG = "/home/adem/graywolf/logs/approval_callbacks.log"


def _parse_log_line(line: str) -> dict | None:
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(line)
        except Exception:
            return None


def _parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _read_lines(path: str) -> Iterable[dict]:
    p = Path(path)
    if not p.exists():
        return []
    out: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        parsed = _parse_log_line(line)
        if not parsed:
            continue
        out.append(parsed)
    return out


def get_replan_stats(log_path: str = REPLAN_LOG) -> dict:
    entries = list(_read_lines(log_path))
    total = len(entries)
    analysis = Counter()
    approvals = Counter()
    events = Counter()
    latest = entries[-1] if entries else None

    for entry in entries:
        events.update([entry.get("event", "unknown")])
        analysis_status = (entry.get("analysis") or {}).get("status")
        analysis.update([analysis_status or "unknown"])
        approval_request = entry.get("approval_request") or {}
        approvals.update([approval_request.get("status") or "missing"])

    processed_count = sum(1 for entry in entries if entry.get("processed_by_phase265"))
    pending_count = sum(
        1
        for entry in entries
        if (entry.get("approval_request") or {}).get("status") == "GRANTED"
        and not entry.get("processed_by_phase265")
    )

    latencies: list[float] = []
    for entry in entries:
        approval_request = entry.get("approval_request") or {}
        created = _parse_ts(approval_request.get("created_at"))
        granted = _parse_ts(approval_request.get("granted_at"))
        if created and granted:
            latencies.append((granted - created).total_seconds())

    if latencies:
        latency_info = {
            "count": len(latencies),
            "avg_seconds": sum(latencies) / len(latencies),
            "max_seconds": max(latencies),
            "long_count": sum(1 for value in latencies if value > 120),
            "latest_seconds": latencies[-1],
        }
    else:
        latency_info = {
            "count": 0,
            "avg_seconds": None,
            "max_seconds": None,
            "long_count": 0,
            "latest_seconds": None,
        }

    return {
        "total_events": total,
        "events_by_type": dict(events),
        "analysis_status": dict(analysis),
        "approval_status": dict(approvals),
        "latest": latest,
        "processed_count": processed_count,
        "pending_count": pending_count,
        "approval_latency": latency_info,
        "approval_latency_threshold_seconds": 120,
    }


def get_approval_callback_summary(log_path: str = APPROVAL_LOG) -> dict:
    entries = list(_read_lines(log_path))
    total = len(entries)
    actions = Counter()
    statuses = Counter()

    for entry in entries:
        actions.update([entry.get("action") or "unknown"])
        statuses.update([entry.get("payload", {}).get("status") or "unknown"])

    return {
        "total_callbacks": total,
        "actions": dict(actions),
        "statuses": dict(statuses),
        "latest": entries[-1] if entries else None,
    }


def print_health_report(replan_log: str = REPLAN_LOG, approval_log: str = APPROVAL_LOG) -> None:
    replan = get_replan_stats(replan_log)
    callbacks = get_approval_callback_summary(approval_log)

    print("=== Replan Bridge Summary ===")
    print(f"Toplam olay: {replan['total_events']}")
    print("Analiz statüleri:")
    for status, count in sorted(replan["analysis_status"].items()):
        print(f"  {status}: {count}")
    print("Approval statüleri:")
    for status, count in sorted(replan["approval_status"].items()):
        print(f"  {status}: {count}")
    print(f"Processed: {replan['processed_count']} | Pending (GRANTED): {replan['pending_count']}")
    latest = replan.get("latest")
    if latest:
        print(f"Son event: {latest.get('event')} at {latest.get('ts')} (approval {latest.get('approval_request', {}).get('status')})")

    latency = replan.get("approval_latency", {})
    if latency.get("count"):
        avg = latency.get("avg_seconds") or 0
        max_latency = latency.get("max_seconds") or 0
        long_count = latency.get("long_count", 0)
        print(
            f"Onay gecikmesi ortalama {avg:.1f}s | max {max_latency:.1f}s | "
            f"{long_count} entry {replan.get('approval_latency_threshold_seconds')}s üstünde"
        )

    print("\n=== Callback Activity ===")
    print(f"Toplam callback: {callbacks['total_callbacks']}")
    print("Callback eylemleri:")
    for action, count in sorted(callbacks["actions"].items()):
        print(f"  {action}: {count}")
    print("Callback statüleri:")
    for status, count in sorted(callbacks["statuses"].items()):
        print(f"  {status}: {count}")
    latest_callback = callbacks.get("latest")
    if latest_callback:
        print(f"Son callback: {latest_callback.get('action')} -> {latest_callback.get('payload', {}).get('status')} at {latest_callback.get('payload', {}).get('metadata', {}).get('ts')}" )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replan Approval Health Summary")
    parser.add_argument("--replan-log", default=REPLAN_LOG)
    parser.add_argument("--approval-log", default=APPROVAL_LOG)
    args = parser.parse_args()

    print_health_report(args.replan_log, args.approval_log)
