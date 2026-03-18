import json
from pathlib import Path

from monitor.approval_health import get_approval_callback_summary, get_replan_stats


def _write_json_lines(tmp_path, entries):
    path = tmp_path / "sample.log"
    path.write_text("\n".join(json.dumps(entry, ensure_ascii=False) for entry in entries) + "\n")
    return path


def test_get_replan_stats(tmp_path):
    entries = [
        {
            "ts": "2026-03-11T12:00:00+00:00",
            "event": "REPLAN_READY",
            "analysis": {"status": "ok"},
            "approval_request": {
                "status": "PENDING",
                "request_id": "req-1",
                "created_at": "2026-03-11T12:00:00+00:00",
            },
        },
        {
            "ts": "2026-03-11T12:05:00+00:00",
            "event": "REPLAN_EXECUTED",
            "analysis": {"status": "error"},
            "approval_request": {
                "status": "GRANTED",
                "request_id": "req-1",
                "created_at": "2026-03-11T12:00:00+00:00",
                "granted_at": "2026-03-11T12:05:00+00:00",
            },
        },
    ]
    log_path = _write_json_lines(tmp_path, entries)
    stats = get_replan_stats(str(log_path))

    assert stats["total_events"] == 2
    assert stats["events_by_type"]["REPLAN_READY"] == 1
    assert stats["analysis_status"]["ok"] == 1
    assert stats["analysis_status"]["error"] == 1
    assert stats["approval_status"]["PENDING"] == 1
    assert stats["approval_status"]["GRANTED"] == 1
    assert stats["latest"]["event"] == "REPLAN_EXECUTED"
    assert stats["processed_count"] == 0
    assert stats["pending_count"] == 1

    latency = stats["approval_latency"]
    assert latency["count"] == 1
    assert latency["avg_seconds"] == 300
    assert latency["long_count"] == 1


def test_get_approval_callback_summary(tmp_path):
    entries = [
        {"action": "approval.grant", "payload": {"status": "granted"}},
        {"action": "approval.deny", "payload": {"status": "denied"}},
        {"action": "approval.grant", "payload": {"status": "granted"}},
    ]
    log_path = _write_json_lines(tmp_path, entries)
    summary = get_approval_callback_summary(str(log_path))

    assert summary["total_callbacks"] == 3
    assert summary["actions"]["approval.grant"] == 2
    assert summary["actions"]["approval.deny"] == 1
    assert summary["statuses"]["granted"] == 2
    assert summary["statuses"]["denied"] == 1
    assert summary["latest"]["action"] == "approval.grant"
