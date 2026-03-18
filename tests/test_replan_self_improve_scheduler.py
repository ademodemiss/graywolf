import json
from pathlib import Path

from monitor.replan_self_improve_scheduler import run_scheduler, _read_json_lines


def _write_log_entries(path: Path, entries: list[dict]) -> Path:
    path.write_text("\n".join(json.dumps(entry, ensure_ascii=False) for entry in entries) + "\n")
    return path


def test_scheduler_marks_granted_entries(tmp_path):
    replan_log = tmp_path / "self_improve_replan.log"
    scheduler_log = tmp_path / "scheduler.log"
    entries = [
        {
            "ts": "2026-03-11T12:00:00+00:00",
            "event": "REPLAN_READY",
            "payload": {"workflow_name": "phase265"},
            "approval_request": {"status": "GRANTED", "request_id": "req-1", "created_at": "2026-03-11T12:00:00+00:00", "granted_at": "2026-03-11T12:05:00+00:00"},
        },
        {
            "ts": "2026-03-11T12:10:00+00:00",
            "event": "REPLAN_READY",
            "payload": {"workflow_name": "phase265"},
            "approval_request": {"status": "PENDING", "request_id": "req-2"},
        },
    ]
    _write_log_entries(replan_log, entries)

    result = run_scheduler(str(replan_log), str(scheduler_log), limit=2)

    assert result["processed"] == 1
    assert result["pending_before"] == 1
    assert result["pending_after"] == 0
    assert result["jobs"] == 1

    updated_entries = _read_json_lines(replan_log)
    assert updated_entries[0].get("processed_by_phase265")
    assert "scheduler" in updated_entries[0]["processed_by_phase265"]

    log_lines = scheduler_log.read_text().strip().splitlines()
    assert len(log_lines) == 1
    log_entry = json.loads(log_lines[0])
    assert log_entry["request_id"] == "req-1"
    assert log_entry["workflow"] == "phase265"


def test_scheduler_respects_limit(tmp_path):
    replan_log = tmp_path / "self_improve_replan.log"
    scheduler_log = tmp_path / "scheduler.log"
    entries = [
        {
            "ts": "2026-03-11T12:00:00+00:00",
            "event": "REPLAN_READY",
            "payload": {"workflow_name": f"phase265-{i}"},
            "approval_request": {"status": "GRANTED", "request_id": f"req-{i}"},
        }
        for i in range(5)
    ]
    _write_log_entries(replan_log, entries)

    result = run_scheduler(str(replan_log), str(scheduler_log), limit=2)

    assert result["processed"] == 2
    assert result["pending_before"] == 5
    assert result["pending_after"] == 3
    log_lines = scheduler_log.read_text().strip().splitlines()
    assert len(log_lines) == 2
