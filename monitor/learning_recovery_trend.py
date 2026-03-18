import argparse
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Iterable, Sequence

from monitor.telegram_alert import send_telegram_message

LEARNING_LOG = Path("/home/adem/graywolf/logs/self_improve_learning.log")
TREND_LOG = Path("/home/adem/graywolf/logs/learning_recovery_trend.log")
DEFAULT_WINDOW_HOURS = 12
SUCCESS_STATUSES = {"completed", "success", "ok", "done"}
FAILURE_STATUSES = {"failed", "error", "denied", "failure", "reject"}
RELIABILITY_WARNING = 65.0
RELIABILITY_CRITICAL = 50.0
PENDING_WARNING = 3
PROCESSED_FLAG = "processed_by_phase265"
LEARNING_FLAG = "processed_by_phase266"
MAX_REASONABLE_DURATION_MS = 6 * 60 * 60 * 1000  # 6 saat


def _parse_log_line(line: str) -> dict | None:
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def _read_log_entries(path: Path | str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    entries: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        parsed = _parse_log_line(line)
        if parsed:
            entries.append(parsed)
    return entries


def _parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _window_entries(entries: Sequence[dict], hours: int) -> list[dict]:
    now = datetime.now(timezone.utc)
    threshold = now - timedelta(hours=hours)
    result: list[dict] = []
    for entry in entries:
        ts = _parse_ts(entry.get("ts"))
        if ts and ts >= threshold:
            result.append(entry)
    return result


def _normalize_duration_ms(value: object) -> float | None:
    if not isinstance(value, (int, float)):
        return None
    duration = float(value)
    if duration < 0:
        return None
    if duration > MAX_REASONABLE_DURATION_MS:
        return None
    return duration


def _build_stats(entries: Sequence[dict]) -> dict:
    total = len(entries)
    success_count = 0
    failure_count = 0
    warning_count = 0
    reliability_scores: list[float] = []
    duration_ms: list[float] = []
    start_sources: Counter[str] = Counter()
    learning_events: Counter[str] = Counter()
    start_sources_raw = Counter()
    for entry in entries:
        status = (entry.get("learning_status") or "").lower()
        if status in SUCCESS_STATUSES:
            success_count += 1
        elif status in FAILURE_STATUSES:
            failure_count += 1
        else:
            warning_count += 1
        category = (entry.get("learning_feedback_category") or "").lower()
        if category == "warning":
            warning_count += 1
        score = entry.get("learning_reliability_score")
        if isinstance(score, (int, float)):
            reliability_scores.append(float(score))
        normalized_duration = _normalize_duration_ms(entry.get("learning_duration_ms"))
        if normalized_duration is not None:
            duration_ms.append(normalized_duration)
        start = entry.get("start_source")
        if isinstance(start, str):
            start_sources[start] += 1
        event = entry.get("learning_event")
        if isinstance(event, str):
            learning_events[event] += 1
    pending = max(total - success_count - failure_count, 0)
    success_rate = (success_count / total * 100) if total else None
    reliability_avg = (sum(reliability_scores) / len(reliability_scores)) if reliability_scores else None
    duration_avg = (sum(duration_ms) / len(duration_ms)) if duration_ms else None
    return {
        "total": total,
        "success": success_count,
        "failure": failure_count,
        "pending": pending,
        "success_rate": success_rate,
        "reliability": reliability_avg,
        "duration_ms_avg": duration_avg,
        "warning_count": warning_count,
        "start_sources": dict(start_sources),
        "events": dict(learning_events),
    }


def _latest_entry(entries: Sequence[dict]) -> dict | None:
    if not entries:
        return None
    return entries[-1]


def _gather_reasons(stats: dict) -> list[str]:
    reasons: list[str] = []
    reliability = stats.get("reliability")
    pending = stats.get("pending")
    warning_count = stats.get("warning_count")
    if isinstance(reliability, float):
        if reliability < RELIABILITY_CRITICAL:
            reasons.append(f"Reliability {reliability:.1f}% < {RELIABILITY_CRITICAL}")
        elif reliability < RELIABILITY_WARNING:
            reasons.append(f"Reliability {reliability:.1f}% < {RELIABILITY_WARNING}")
    if isinstance(pending, int) and pending > PENDING_WARNING:
        reasons.append(f"Pending job sayısı {pending} > {PENDING_WARNING}")
    if isinstance(warning_count, int) and warning_count > 0:
        reasons.append(f"Warning feedback {warning_count} adet")
    if not reasons:
        reasons.append("No trend alarms")
    return reasons


def _determine_severity(stats: dict) -> str:
    reliability = stats.get("reliability")
    pending = stats.get("pending")
    if isinstance(reliability, float) and reliability < RELIABILITY_CRITICAL:
        return "critical"
    if isinstance(pending, int) and pending > PENDING_WARNING:
        return "warning"
    if isinstance(reliability, float) and reliability < RELIABILITY_WARNING:
        return "warning"
    return "info"


def _build_message(stats: dict, latest: dict | None, severity: str, window: int, reasons: Sequence[str]) -> str:
    success_rate = stats.get("success_rate") or 0
    pending = stats.get("pending") or 0
    reliability = stats.get("reliability")
    lines = [f"Phase 272 Trend Watcher ({window} saat)"]
    if reliability is not None:
        lines.append(f"Success rate: {success_rate:.1f}% | Pending: {pending} | Reliability: {reliability:.1f}%")
    else:
        lines.append(f"Success rate: {success_rate:.1f}% | Pending: {pending}")
    if latest:
        lines.append(f"Last feedback: {latest.get('learning_feedback') or 'bilinmeyen'}")
        last_duration = _normalize_duration_ms(latest.get("learning_duration_ms"))
        duration_text = f"{int(last_duration)}" if last_duration is not None else "bilinmeyen"
        lines.append(f"Last event: {latest.get('learning_event') or 'bilinmeyen'} | Duration: {duration_text} ms")
    lines.append(f"Severity: {severity.upper()} | Reasons: {', '.join(reasons[:3])}")
    if len(reasons) > 3:
        lines[-1] += f" (+{len(reasons) - 3} daha)"
    return "\n".join(lines)


def _build_trend_record(stats: dict, latest: dict | None, severity: str, reasons: Sequence[str]) -> dict:
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "window_hours": int(stats.get("window_hours", DEFAULT_WINDOW_HOURS)),
        "stats": stats,
        "severity": severity,
        "reasons": list(reasons),
        "latest_feedback": latest.get("learning_feedback") if latest else None,
        "latest_event": latest.get("learning_event") if latest else None,
        "last_duration_ms": _normalize_duration_ms(latest.get("learning_duration_ms")) if latest else None,
        "start_sources": stats.get("start_sources"),
        "learning_events": stats.get("events"),
    }
    if latest:
        if latest.get(PROCESSED_FLAG):
            record[PROCESSED_FLAG] = latest.get(PROCESSED_FLAG)
        if latest.get(LEARNING_FLAG):
            record[LEARNING_FLAG] = latest.get(LEARNING_FLAG)
    return record


def _write_trend_log(record: dict, path: Path | str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as out:
        out.write(json.dumps(record, ensure_ascii=False) + "\n")


def _should_send_telegram(severity: str) -> bool:
    return severity in {"warning", "critical"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 272 learning trend monitor")
    parser.add_argument("--learning-log", default=str(LEARNING_LOG))
    parser.add_argument("--trend-log", default=str(TREND_LOG))
    parser.add_argument("--window-hours", type=int, default=DEFAULT_WINDOW_HOURS)
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    entries = _read_log_entries(args.learning_log)
    window = _window_entries(entries, args.window_hours)
    stats = _build_stats(window)
    stats["window_hours"] = args.window_hours
    latest = _latest_entry(window) if window else _latest_entry(entries)
    reasons = _gather_reasons(stats)
    severity = _determine_severity(stats)
    message = _build_message(stats, latest, severity, args.window_hours, reasons)
    record = _build_trend_record(stats, latest or {}, severity, reasons)
    print(message)
    if not args.dry_run:
        _write_trend_log(record, args.trend_log)
    if args.telegram and not args.dry_run and _should_send_telegram(severity):
        send_telegram_message(message)


if __name__ == "__main__":
    main()
