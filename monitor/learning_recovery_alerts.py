import argparse
import datetime
import json
from pathlib import Path
from typing import Iterable, Sequence

from monitor.telegram_alert import send_telegram_message

INSIGHTS_PATH = Path("/home/adem/graywolf/logs/learning_recovery_insights.json")
ALERTS_LOG = Path("/home/adem/graywolf/logs/learning_recovery_alerts.log")

RELIABILITY_WARNING = 60.0
RELIABILITY_CRITICAL = 40.0
PENDING_THRESHOLD = 3
LEARNING_FLAG = "processed_by_phase266"
PROCESSED_FLAG = "processed_by_phase271"


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def _write_alert(entry: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as out:
        out.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _gather_reasons(summary: dict, insights: Sequence[dict]) -> tuple[str, list[str]]:
    avg = summary.get("avg_reliability")
    pending = summary.get("pending")
    severity = "info"
    reasons: list[str] = []

    if isinstance(avg, (int, float)):
        if avg < RELIABILITY_CRITICAL:
            severity = "critical"
            reasons.append(f"Avg reliability {avg:.1f}% < {RELIABILITY_CRITICAL}")
        elif avg < RELIABILITY_WARNING:
            severity = "warning"
            reasons.append(f"Avg reliability {avg:.1f}% < {RELIABILITY_WARNING}")
    if isinstance(pending, int) and pending > PENDING_THRESHOLD:
        if severity != "critical":
            severity = "warning"
        reasons.append(f"Pending jobs {pending} > {PENDING_THRESHOLD}")
    for insight in insights:
        insight_severity = (insight.get("severity") or "").lower()
        title = insight.get("title") or insight.get("workflow") or insight.get("reason") or "insight"
        if insight_severity == "critical":
            severity = "critical"
            reasons.append(title)
        elif insight_severity == "warning" and severity != "critical":
            severity = "warning"
            reasons.append(title)
    if not reasons:
        reliability_status = f"avg reliability {avg:.1f}%" if isinstance(avg, (int, float)) else "no data"
        reasons.append(f"Durum normal ({reliability_status})")
    return severity, reasons


def _build_message(severity: str, summary: dict, reasons: Sequence[str], insights: Sequence[dict]) -> str:
    severity_label = severity.upper()
    avg = summary.get("avg_reliability")
    pending = summary.get("pending")
    last_insight = insights[-1] if insights else {}
    last_title = last_insight.get("title") or last_insight.get("workflow") or "insight yok"
    lines = [f"Reliability alarm [{severity_label}]", f"Ortalama reliability: {avg:.1f}%" if avg is not None else "Reliability: veri yok"]
    if isinstance(pending, int):
        lines.append(f"Pending: {pending}")
    lines.append(f"Son insight: {last_title}")
    lines.append("Sebep:")
    for reason in reasons[:4]:
        lines.append(f"- {reason}")
    if len(reasons) > 4:
        lines.append(f"- +{len(reasons) - 4} diğer sebep")
    return "\n".join(lines)


def _should_send_alert(severity: str) -> bool:
    return severity in {"warning", "critical"}


def _append_insight_titles(insights: Sequence[dict]) -> list[str]:
    titles = []
    for insight in insights:
        t = insight.get("title") or insight.get("workflow")
        if t:
            titles.append(t)
    return titles


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 271 learning reliability alerts")
    parser.add_argument("--insights", type=Path, default=INSIGHTS_PATH, help="learning recovery insights path")
    parser.add_argument("--alerts-log", type=Path, default=ALERTS_LOG, help="alerts log path")
    parser.add_argument("--telegram", action="store_true", help="Telegram uyarısı gönder")
    parser.add_argument("--dry-run", action="store_true", help="Telegram gönderimini atla")
    args = parser.parse_args()

    record = _load_json(args.insights)
    if not record:
        print("learning_recovery_insights.json bulunamadı veya boş.")
        return

    summary = record.get("summary", {})
    insights = record.get("insights", [])
    suggestions = record.get("suggestions", {})

    severity, reasons = _gather_reasons(summary, insights)
    message = _build_message(severity, summary, reasons, insights)
    alert_entry = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "severity": severity,
        "avg_reliability": summary.get("avg_reliability"),
        "pending": summary.get("pending"),
        "reasons": reasons,
        "insights": _append_insight_titles(insights),
        "suggestions": suggestions,
        "learning_flag": LEARNING_FLAG,
        "processed_flag": PROCESSED_FLAG,
    }
    _write_alert(alert_entry, args.alerts_log)
    print(message)

    if args.telegram and not args.dry_run and _should_send_alert(severity):
        send_telegram_message(message)


if __name__ == "__main__":
    main()
