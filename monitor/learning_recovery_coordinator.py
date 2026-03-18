import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from statistics import mean
from typing import Iterable, Sequence

from monitor.telegram_alert import send_telegram_message

LEARNING_RECOVERY_LOG = Path("/home/adem/graywolf/logs/learning_recovery.log")
LEARNING_RECOVERY_SUGGESTIONS = Path("/home/adem/graywolf/logs/learning_recovery_suggestions.json")
LEARNING_RECOVERY_SUMMARY = Path("/home/adem/graywolf/logs/learning_recovery_summary.log")


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
    out: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _window_entries(entries: Sequence[dict], hours: int) -> list[dict]:
    now = datetime.now(timezone.utc)
    threshold = now - timedelta(hours=hours)
    out: list[dict] = []
    for entry in entries:
        ts = _parse_ts(entry.get("ts"))
        if not ts:
            continue
        if ts >= threshold:
            out.append(entry)
    return out


def _read_suggestions(path: Path | str) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _aggregate_recovery(entries: list[dict]) -> dict:
    autopilot = [e for e in entries if e.get("action") == "auto_retry"]
    reliability_scores = [e.get("reliability_score") for e in autopilot if isinstance(e.get("reliability_score"), (int, float))]
    avg_reliability = mean(reliability_scores) if reliability_scores else None
    return {
        "autopilot_retries": len(autopilot),
        "avg_reliability": avg_reliability,
        "last_retry": autopilot[-1] if autopilot else None,
    }


def _append_summary(entry: dict, path: Path | str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _build_summary_message(summary: dict, suggestions: dict, window_hours: int) -> str:
    lines = [
        f"Phase 269 Learning Recovery Overview ({window_hours} saat)"
    ]
    if summary["autopilot_retries"]:
        lines.append(
            f"Autopilot retry sayısı: {summary['autopilot_retries']} | ort. reliability: {summary['avg_reliability']:.1f}%" if summary["avg_reliability"] is not None else f"Autopilot retry sayısı: {summary['autopilot_retries']}"
        )
        last = summary.get("last_retry")
        if last:
            last_id = last.get("new_request_id") or last.get("original_request_id")
            lines.append(
                f"Son retry: {last_id} (reason={last.get('reason')}) | failures={last.get('failure_count')} | pending={last.get('pending')}"
            )
    else:
        lines.append("Bu pencere içinde otomatik retry tetiklenmedi.")

    autop = suggestions.get("autopilot", {})
    trend = suggestions.get("trend", {})
    if autop.get("summary"):
        lines.append(f"Dashboard önerisi (autopilot): {autop['summary']}")
    if trend.get("summary"):
        lines.append(f"Dashboard önerisi (trend): {trend['summary']}")
    if not autop.get("summary") and not trend.get("summary"):
        lines.append("Dashboard önerisi yok." )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Learning recovery coordination summary")
    parser.add_argument("--recovery-log", default=str(LEARNING_RECOVERY_LOG))
    parser.add_argument("--suggestions", default=str(LEARNING_RECOVERY_SUGGESTIONS))
    parser.add_argument("--summary-log", default=str(LEARNING_RECOVERY_SUMMARY))
    parser.add_argument("--window-hours", type=int, default=24)
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    entries = _read_json_lines(args.recovery_log)
    window_entries = _window_entries(entries, args.window_hours)
    summary = _aggregate_recovery(window_entries)
    suggestions = _read_suggestions(args.suggestions)
    message = _build_summary_message(summary, suggestions, args.window_hours)
    print(message)

    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "window_hours": args.window_hours,
        "autopilot_retries": summary["autopilot_retries"],
        "avg_reliability": summary["avg_reliability"],
        "last_retry": summary.get("last_retry", {}).get("new_request_id")
        if summary.get("last_retry")
        else None,
        "anti_pattern": suggestions.get("trend", {}).get("alert_message"),
    }

    if not args.dry_run:
        _append_summary(record, args.summary_log)
        if args.telegram:
            send_telegram_message(message)


if __name__ == "__main__":
    main()
