import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from statistics import mean
from typing import Iterable, Sequence

from monitor.telegram_alert import send_telegram_message

LEARNING_RECOVERY_LOG = Path("/home/adem/graywolf/logs/learning_recovery.log")
LEARNING_RECOVERY_SUMMARY = Path("/home/adem/graywolf/logs/learning_recovery_summary.log")
LEARNING_RECOVERY_SUGGESTIONS = Path("/home/adem/graywolf/logs/learning_recovery_suggestions.json")
LEARNING_LOG = Path("/home/adem/graywolf/logs/self_improve_learning.log")
INSIGHTS_OUTPUT = Path("/home/adem/graywolf/logs/learning_recovery_insights.json")
DEFAULT_WINDOW_HOURS = 24
RELIABILITY_THRESHOLD = 60.0
FAILURE_STREAK_THRESHOLD = 3


def _parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


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


def _read_json(path: Path | str) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _window_entries(entries: Sequence[dict], hours: int) -> list[dict]:
    now = datetime.now(timezone.utc)
    threshold = now - timedelta(hours=hours)
    windowed: list[dict] = []
    for entry in entries:
        ts = _parse_ts(entry.get("ts"))
        if not ts:
            continue
        if ts >= threshold:
            windowed.append(entry)
    return windowed


def _workflow_stats(entries: Sequence[dict]) -> dict:
    stats: dict[str, dict] = {}
    for entry in entries:
        workflow = entry.get("workflow") or entry.get("workflow_name") or entry.get("analysis", {}).get("workflow")
        if not workflow:
            continue
        data = stats.setdefault(
            workflow,
            {
                "entries": [],
                "failure_count": 0,
                "warning_count": 0,
                "success_count": 0,
                "reliability_scores": [],
                "last_entry": None,
            },
        )
        data["entries"].append(entry)
        category = entry.get("learning_feedback_category") or entry.get("category") or entry.get("learning_feedback")
        if isinstance(category, str):
            category = category.lower()
        if category == "failure":
            data["failure_count"] += 1
        elif category == "warning":
            data["warning_count"] += 1
        elif category == "success":
            data["success_count"] += 1
        score = entry.get("learning_reliability_score")
        if isinstance(score, (int, float)):
            data["reliability_scores"].append(score)
        data["last_entry"] = entry
    return stats


def _summaries_from_scores(scores: Sequence[float]) -> float | None:
    if not scores:
        return None
    return mean(scores)


def _build_insights(
    summary: dict,
    suggestions: dict,
    learning_stats: dict[str, dict],
    recovery_entries: Sequence[dict],
) -> list[dict]:
    insights: list[dict] = []

    autopilot_section = suggestions.get("autopilot", {})
    if summary.get("autopilot_retries"):
        insights.append(
            {
                "type": "autopilot",
                "title": autopilot_section.get("summary")
                or f"Autopilot retry {summary.get('autopilot_retries')} kez çalıştı",
                "severity": "warning",
                "suggested_action": autopilot_section.get("suggested_action", "izleme"),
                "details": {
                    "reliability_score": autopilot_section.get("reliability_score"),
                    "failure_count": autopilot_section.get("failure_count"),
                    "pending": autopilot_section.get("pending"),
                },
            }
        )

    trend = suggestions.get("trend", {})
    if trend.get("alert_message"):
        insights.append(
            {
                "type": "trend",
                "title": trend["summary"],
                "severity": "critical",
                "suggested_action": trend.get("suggested_action", "manual review"),
                "details": {
                    "alert_message": trend.get("alert_message"),
                    "warning_delta": trend.get("warning_delta"),
                },
            }
        )

    for workflow, data in learning_stats.items():
        avg_reliability = _summaries_from_scores(data["reliability_scores"])
        failure_count = data["failure_count"]
        severity = None
        note = None
        suggested_action = "izleme"
        if failure_count >= FAILURE_STREAK_THRESHOLD or (avg_reliability is not None and avg_reliability < RELIABILITY_THRESHOLD):
            severity = "critical" if failure_count >= FAILURE_STREAK_THRESHOLD or (avg_reliability or 0) < 40 else "warning"
            note = (
                f"{workflow} - failures: {failure_count}, avg reliability: {avg_reliability:.1f}%"
                if avg_reliability is not None
                else f"{workflow} - failures: {failure_count}"
            )
            if failure_count >= FAILURE_STREAK_THRESHOLD:
                suggested_action = "manual review"
            elif avg_reliability is not None and avg_reliability < RELIABILITY_THRESHOLD:
                suggested_action = "increase reliability" if avg_reliability >= 40 else "manual review"
            insights.append(
                {
                    "type": "workflow",  # indicates repeated issues
                    "title": f"{workflow} reliability alarm",
                    "severity": severity,
                    "suggested_action": suggested_action,
                    "details": {
                        "failure_count": failure_count,
                        "avg_reliability": avg_reliability,
                        "last_status": data["last_entry"].get("learning_status")
                        if data["last_entry"]
                        else None,
                    },
                }
            )

    if recovery_entries:
        latest_retry = recovery_entries[-1]
        insights.append(
            {
                "type": "recovery_log",
                "title": "Otomatik retry detayları",
                "severity": "info",
                "suggested_action": "monitor",
                "details": {
                    "reason": latest_retry.get("reason"),
                    "reliability_score": latest_retry.get("reliability_score"),
                    "failure_count": latest_retry.get("failure_count"),
                    "pending": latest_retry.get("pending"),
                },
            }
        )

    return insights


def _build_message(summary: dict, suggestions: dict, insights: list[dict], window_hours: int) -> str:
    lines: list[str] = [f"Phase 270 Learning Recovery Inspector ({window_hours} saat)"]

    if summary:
        lines.append(
            f"Autopilot retries: {summary.get('autopilot_retries', 0)} | Ort. reliability: {summary.get('avg_reliability') or 'n/a'}%"
        )
        if summary.get("last_retry"):
            lines.append(f"Son retry: {summary['last_retry']}")
    if suggestions.get("autopilot", {}).get("summary"):
        lines.append(f"Dashboard önerisi (autopilot): {suggestions['autopilot']['summary']}")
    if suggestions.get("trend", {}).get("summary"):
        lines.append(f"Dashboard önerisi (trend): {suggestions['trend']['summary']}")

    if insights:
        lines.append("Önemli insight’lar:")
        for insight in insights[:3]:
            severity = insight.get("severity", "info")
            lines.append(f"- [{severity}] {insight.get('title')}")
    else:
        lines.append("Önemli insight yok.")

    return "\n".join(lines)


def _write_insights(data: dict, path: Path | str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 270 learning recovery inspector")
    parser.add_argument("--recovery-log", default=str(LEARNING_RECOVERY_LOG))
    parser.add_argument("--summary-log", default=str(LEARNING_RECOVERY_SUMMARY))
    parser.add_argument("--suggestions", default=str(LEARNING_RECOVERY_SUGGESTIONS))
    parser.add_argument("--learning-log", default=str(LEARNING_LOG))
    parser.add_argument("--output", default=str(INSIGHTS_OUTPUT))
    parser.add_argument("--window-hours", type=int, default=DEFAULT_WINDOW_HOURS)
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    recovery_entries = _read_json_lines(args.recovery_log)
    summary_entries = _read_json_lines(args.summary_log)
    suggestions = _read_json(args.suggestions)
    learning_entries = _read_json_lines(args.learning_log)

    window_summaries = _window_entries(summary_entries, args.window_hours)
    summary = window_summaries[-1] if window_summaries else {}

    window_learning = _window_entries(learning_entries, args.window_hours)
    window_recovery = _window_entries(recovery_entries, args.window_hours)
    workflow_stats = _workflow_stats(window_learning)

    insights = _build_insights(summary, suggestions, workflow_stats, window_recovery)
    message = _build_message(summary, suggestions, insights, args.window_hours)

    inspector_record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "window_hours": args.window_hours,
        "summary": summary,
        "suggestions": suggestions,
        "insights": insights,
    }

    print(message)

    if not args.dry_run:
        _write_insights(inspector_record, args.output)
    if args.telegram:
        send_telegram_message(message)
        print("Inspector telegram gönderildi.")


if __name__ == "__main__":
    main()
