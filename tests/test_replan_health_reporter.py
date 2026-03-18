from monitor.replan_health_reporter import build_replan_health_message


def test_build_replan_health_message_includes_expected_sections():
    replan_stats = {
        "total_events": 3,
        "processed_count": 2,
        "pending_count": 1,
        "approval_latency": {
            "count": 1,
            "avg_seconds": 45,
            "max_seconds": 90,
            "long_count": 0,
        },
        "approval_latency_threshold_seconds": 120,
        "latest": {
            "event": "REPLAN_READY",
            "ts": "2026-03-11T12:00:00+00:00",
            "approval_request": {"status": "GRANTED"},
        },
    }
    callback_summary = {
        "total_callbacks": 2,
        "actions": {"approval.grant": 1, "approval.deny": 1},
        "statuses": {"granted": 1, "denied": 1},
        "latest": {"action": "approval.deny"},
    }

    message = build_replan_health_message(replan_stats, callback_summary)

    assert "Toplam olay: 3" in message
    assert "İşlenen replan: 2 | Bekleyen (GRANTED): 1" in message
    assert "Son event: REPLAN_READY" in message
    assert "Onay gecikmesi: ort." in message
    assert "approval.grant: 1, approval.deny: 1" in message
    assert "Callback aktivitesi: toplam 2" in message
    assert "- Son callback: approval.deny" in message
