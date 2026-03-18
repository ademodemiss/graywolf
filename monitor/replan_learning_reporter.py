import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from monitor.telegram_alert import send_telegram_message

LEARNING_LOG = Path("/home/adem/graywolf/logs/self_improve_learning.log")
DEFAULT_WINDOW_HOURS = 24
SUCCESS_STATUSES = {"completed", "success", "ok"}
FAILURE_STATUSES = {"failed", "error", "denied", "failure"}
CATEGORY_SCORES = {"success": 95, "warning": 65, "failure": 20, "unknown": 50}
RELIABILITY_THRESHOLD = 70
PENDING_THRESHOLD = 5


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


def _recent_entries(entries: Sequence[dict], hours: int) -> list[dict]:
    threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent = []
    for entry in entries:
        ts = _parse_ts(entry.get("ts"))
        if ts and ts >= threshold:
            recent.append(entry)
    return recent


def _determine_category(entry: dict) -> str:
    candidate = (entry.get("learning_feedback_category") or "").lower()
    if candidate in CATEGORY_SCORES:
        return candidate
    status = (entry.get("learning_status") or "").lower()
    if status in SUCCESS_STATUSES:
        return "success"
    if status in FAILURE_STATUSES:
        return "failure"
    feedback = (entry.get("learning_feedback") or "").lower()
    for keyword in ["fail", "error", "denied", "reject", "warn", "warning"]:
        if keyword in feedback:
            return "failure" if keyword in ["fail", "error", "denied", "reject"] else "warning"
    return "unknown"


def _entry_reliability_score(entry: dict, category: str) -> int:
    score = entry.get("learning_reliability_score")
    if isinstance(score, (int, float)):
        return int(score)
    return CATEGORY_SCORES.get(category, CATEGORY_SCORES["unknown"])


def build_learning_stats(log_entries: Sequence[dict], window_hours: int = DEFAULT_WINDOW_HOURS) -> dict:
    recent = _recent_entries(log_entries, window_hours)
    total = len(recent)
    status_counter = Counter()
    category_counter = Counter()
    reliability_scores: list[int] = []
    success = 0
    failure = 0
    warning_count = 0

    for entry in recent:
        status = (entry.get("learning_status") or "unknown").lower()
        category = _determine_category(entry)
        status_counter.update([status])
        category_counter.update([category])
        if status in SUCCESS_STATUSES:
            success += 1
        elif status in FAILURE_STATUSES:
            failure += 1
        elif category == "warning":
            warning_count += 1
        reliability_scores.append(_entry_reliability_score(entry, category))

    pending = total - success - failure
    success_rate = (success / total * 100) if total else None
    reliability_score = (sum(reliability_scores) / len(reliability_scores)) if reliability_scores else None
    warning_rate = (warning_count / total * 100) if total else None
    latest_entry = recent[-1] if recent else (log_entries[-1] if log_entries else None)

    last_feedback = "yok"
    last_follow_up = "yok"
    if latest_entry:
        last_feedback = (
            latest_entry.get("learning_feedback")
            or latest_entry.get("analysis_summary")
            or latest_entry.get("workflow")
            or "bilinmeyen"
        )
        last_follow_up = latest_entry.get("learning_follow_up_notes") or "yok"

    return {
        "window_hours": window_hours,
        "total": total,
        "success": success,
        "failure": failure,
        "pending": pending if pending >= 0 else 0,
        "success_rate": success_rate,
        "reliability_score": reliability_score,
        "warning_rate": warning_rate,
        "failure_count": failure,
        "latest_status": (latest_entry or {}).get("learning_status") if latest_entry else None,
        "latest_feedback": last_feedback,
        "latest_follow_up": last_follow_up,
        "status_breakdown": dict(status_counter),
        "category_breakdown": dict(category_counter),
    }


def build_learning_message(stats: dict) -> str:
    total = stats.get("total", 0)
    success = stats.get("success", 0)
    failure = stats.get("failure", 0)
    pending = stats.get("pending", 0)
    success_rate = stats.get("success_rate")
    reliability_score = stats.get("reliability_score")
    warning_rate = stats.get("warning_rate")
    latest_feedback = stats.get("latest_feedback") or "yok"
    latest_follow_up = stats.get("latest_follow_up") or "yok"
    latest_status = stats.get("latest_status") or "bilinmeyen"
    window = stats.get("window_hours")

    lines = [
        "Phase 267 Learning Feedback Özeti",
        f"Son {window} saat içinde {total} job incelendi.",
        f"Başarı oranı: {success_rate:.1f}% ({success} başarılı / {total} toplam)" if success_rate is not None else "Başarı oranı: veri yok",
        f"Reliability score: {reliability_score:.1f}%" if reliability_score is not None else "Reliability score: veri yok",
        f"Warning rate: {warning_rate:.1f}% | Failures: {failure} | Pending: {pending}" if warning_rate is not None else f"Failures: {failure} | Pending: {pending}",
        f"Son statü: {latest_status} | feedback: {latest_feedback}",
        f"Son follow-up notları: {latest_follow_up}",
    ]

    return "\n".join(lines)


def _should_send_alert(stats: dict) -> bool:
    reliability = stats.get("reliability_score")
    pending = stats.get("pending", 0)
    if reliability is not None and reliability < RELIABILITY_THRESHOLD:
        return True
    if pending > PENDING_THRESHOLD:
        return True
    return False


def _build_alert_message(stats: dict) -> str:
    parts = []
    reliability = stats.get("reliability_score")
    pending = stats.get("pending", 0)
    if reliability is not None and reliability < RELIABILITY_THRESHOLD:
        parts.append(f"Reliability %70'nin altında: {reliability:.1f}%")
    if pending > PENDING_THRESHOLD:
        parts.append(f"Pending job sayısı {pending} (> {PENDING_THRESHOLD})")
    extra = " | ".join(parts)
    return f"Phase 267 uyarısı: {extra}" if extra else "Phase 267 uyarısı: action required"


def print_learning_summary(log_path: Path | str, hours: int, telegram: bool, dry_run: bool) -> dict:
    entries = _read_log_entries(log_path)
    stats = build_learning_stats(entries, hours)
    message = build_learning_message(stats)
    print(message)
    if telegram and not dry_run:
        result = send_telegram_message(message)
        print(f"telegram = {result}")
        if _should_send_alert(stats):
            alert = _build_alert_message(stats)
            alert_result = send_telegram_message(alert)
            print(f"alert telegram = {alert_result}")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 266 learning raporu")
    parser.add_argument("--log", default=LEARNING_LOG, help="Learning log yolunu belirt")
    parser.add_argument("--hours", type=int, default=DEFAULT_WINDOW_HOURS, help="Kaç saatlik pencere" )
    parser.add_argument("--telegram", action="store_true", help="Telegram kanalına gönder")
    parser.add_argument("--dry-run", action="store_true", help="Telegram gönderimini atla")
    args = parser.parse_args()
    print_learning_summary(args.log, args.hours, args.telegram, args.dry_run)


if __name__ == "__main__":
    main()
