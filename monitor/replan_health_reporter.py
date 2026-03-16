import argparse
from typing import Any

from monitor.approval_health import (
    APPROVAL_LOG,
    REPLAN_LOG,
    get_approval_callback_summary,
    get_replan_stats,
)
from monitor.telegram_alert import send_telegram_message


MessageType = dict[str, Any]


def build_replan_health_message(replan_stats: MessageType, callback_summary: MessageType | None = None) -> str:
    total = replan_stats.get("total_events", 0)
    processed = replan_stats.get("processed_count", 0)
    pending = replan_stats.get("pending_count", 0)
    threshold = replan_stats.get("approval_latency_threshold_seconds", 0)
    latency = replan_stats.get("approval_latency") or {}
    latency_count = latency.get("count", 0)
    avg_latency = latency.get("avg_seconds")
    max_latency = latency.get("max_seconds")
    long_count = latency.get("long_count", 0)
    avg_latency_display = avg_latency if avg_latency is not None else 0
    max_latency_display = max_latency if max_latency is not None else 0
    latest = replan_stats.get("latest") or {}
    latest_event = latest.get("event") or "bilinmiyor"
    latest_ts = latest.get("ts") or "bilinmiyor"
    latest_status = (latest.get("approval_request") or {}).get("status") or "bilinmiyor"

    lines = [
        "Replan Bridge Sağlık Raporu",
        f"Toplam olay: {total}",
        f"İşlenen replan: {processed} | Bekleyen (GRANTED): {pending}",
        f"Son event: {latest_event} @ {latest_ts} (approval: {latest_status})",
    ]

    if latency_count:
        lines.append(
            f"Onay gecikmesi: ort. {avg_latency_display:.1f}s | maks {max_latency_display:.1f}s | {long_count} entry {threshold}s üstünde"
        )
    else:
        lines.append("Onay gecikmesi: veri yok")

    if callback_summary:
        actions = callback_summary.get("actions") or {}
        grants = actions.get("approval.grant", 0)
        denies = actions.get("approval.deny", 0)
        statuses = callback_summary.get("statuses") or {}
        granted_statuses = statuses.get("granted", 0)
        denied_statuses = statuses.get("denied", 0)
        latest_callback = (callback_summary.get("latest") or {}).get("action") or "yok"
        lines.extend(
            [
                f"Callback aktivitesi: toplam {callback_summary.get('total_callbacks', 0)}",  # noqa: WPS221
                f"- approval.grant: {grants}, approval.deny: {denies}",
                f"- granted status: {granted_statuses}, denied status: {denied_statuses}",
                f"- Son callback: {latest_callback}",
            ]
        )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Replan bridge sağlık raporu")
    parser.add_argument("--replan-log", default=REPLAN_LOG)
    parser.add_argument("--approval-log", default=APPROVAL_LOG)
    parser.add_argument("--telegram", action="store_true", help="Telegram kanalına gönder")
    parser.add_argument("--dry-run", action="store_true", help="Telegram gönderimini atla")
    args = parser.parse_args()

    replan_stats = get_replan_stats(args.replan_log)
    callback_summary = get_approval_callback_summary(args.approval_log)
    message = build_replan_health_message(replan_stats, callback_summary)
    print(message)

    if args.telegram and not args.dry_run:
        result = send_telegram_message(message)
        print(f"telegram = {result}")


if __name__ == "__main__":
    main()
