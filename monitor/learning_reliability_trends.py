import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from monitor.replan_learning_reporter import (
    _determine_category,
    _entry_reliability_score,
    _parse_ts,
    _read_log_entries,
)
from monitor.telegram_alert import send_telegram_message

LEARNING_LOG = Path("/home/adem/graywolf/logs/self_improve_learning.log")
SUGGESTIONS_PATH = Path("/home/adem/graywolf/logs/learning_recovery_suggestions.json")
DEFAULT_WINDOW_HOURS = 24
WARNING_DELTA_THRESHOLD = 10.0


def _load_suggestions(path: Path | str = SUGGESTIONS_PATH) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _write_suggestions(data: dict, path: Path | str = SUGGESTIONS_PATH) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _update_suggestions_section(section: str, payload: dict, path: Path | str = SUGGESTIONS_PATH) -> None:
    data = _load_suggestions(path)
    data[section] = payload
    data["ts"] = datetime.now(timezone.utc).isoformat()
    _write_suggestions(data, path)


def _window_entries(entries: list[dict], hours: int, offset_hours: int = 0) -> list[dict]:
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=hours + offset_hours)
    end = now - timedelta(hours=offset_hours)
    windowed: list[dict] = []
    for entry in entries:
        ts = _parse_ts(entry.get("ts"))
        if not ts:
            continue
        if start <= ts < end:
            windowed.append(entry)
    return windowed


def _compute_window_stats(entries: list[dict]) -> dict:
    if not entries:
        return {"warning_rate": None, "reliability_score": None, "count": 0}
    warning_count = 0
    reliability_scores: list[float] = []
    for entry in entries:
        category = _determine_category(entry)
        if category == "warning":
            warning_count += 1
        reliability_scores.append(_entry_reliability_score(entry, category))
    total = len(entries)
    avg_score = sum(reliability_scores) / len(reliability_scores) if reliability_scores else None
    warning_rate = (warning_count / total * 100) if total else None
    return {
        "warning_rate": warning_rate,
        "reliability_score": avg_score,
        "count": total,
    }


def _build_trend_summary(current: dict, previous: dict) -> str:
    curr_warn = current.get("warning_rate")
    prev_warn = previous.get("warning_rate")
    if curr_warn is None:
        return "Yeterli veri yok."
    parts: list[str] = []
    if prev_warn is not None:
        delta = curr_warn - prev_warn
        parts.append(f"Warning rate {curr_warn:.1f}% (önceki {prev_warn:.1f}%, fark {delta:+.1f} puan)")
    else:
        parts.append(f"Warning rate {curr_warn:.1f}% (önceki veri yok)")
    reliability = current.get("reliability_score")
    if reliability is not None:
        parts.append(f"Ortalama reliability {reliability:.1f}%")
    return " | ".join(parts)


def _build_alert_message(current: dict, previous: dict) -> Optional[str]:
    curr = current.get("warning_rate")
    prev = previous.get("warning_rate")
    if curr is None or prev is None:
        return None
    delta = curr - prev
    if delta >= WARNING_DELTA_THRESHOLD:
        return (
            f"Phase 268 Predictive Alert: "
            f"warning rate {prev:.1f}% → {curr:.1f}% (+{delta:.1f} puan). Kontrollere göz at."
        )
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 268 reliability trends")
    parser.add_argument("--log", default=str(LEARNING_LOG))
    parser.add_argument("--window-hours", type=int, default=DEFAULT_WINDOW_HOURS)
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--suggestions", default=str(SUGGESTIONS_PATH))
    args = parser.parse_args()

    entries = _read_log_entries(args.log)
    if not entries:
        print("Öğrenme logları bulunamadı.")
        return

    current_entries = _window_entries(entries, args.window_hours, offset_hours=0)
    previous_entries = _window_entries(entries, args.window_hours, offset_hours=args.window_hours)
    current_stats = _compute_window_stats(current_entries)
    previous_stats = _compute_window_stats(previous_entries)

    summary = _build_trend_summary(current_stats, previous_stats)
    alert_message = _build_alert_message(current_stats, previous_stats)

    warning_delta = (
        current_stats.get("warning_rate")
        - (previous_stats.get("warning_rate") or 0)
        if current_stats.get("warning_rate") is not None
        else None
    )
    trend_payload = {
        "summary": summary,
        "window_hours": args.window_hours,
        "current_warning_rate": current_stats.get("warning_rate"),
        "previous_warning_rate": previous_stats.get("warning_rate"),
        "warning_delta": warning_delta,
        "reliability_score": current_stats.get("reliability_score"),
        "alert_sent": bool(alert_message),
        "alert_message": alert_message,
        "suggested_action": "manual review" if alert_message else "izleme",
    }
    _update_suggestions_section("trend", trend_payload, args.suggestions)

    print(summary)
    if alert_message and args.telegram:
        send_telegram_message(alert_message)
        print("Predictive alert telegram gönderildi.")


if __name__ == "__main__":
    main()
