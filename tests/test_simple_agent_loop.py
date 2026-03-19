from pathlib import Path

from agent.simple_agent_loop import build_plan, run_agent_loop, wait_for_task_completion


def test_build_plan_returns_3_to_5_steps():
    plan = build_plan("bana bir program yap", max_steps=5)
    assert 3 <= len(plan) <= 5


def test_run_agent_loop_low_risk_success():
    def fake_runner(step: str, idx: int, total: int) -> dict:
        return {"status": "completed", "summary": f"step {idx} tamamlandı"}

    out = run_agent_loop("sistemde sağlık kontrolü yap", step_runner=fake_runner, max_steps=3)
    assert out["status"] == "ok"
    assert out["completed_steps"] == 3
    assert len(out["trace"]) == 3
    assert out["final"]["state"] == "tamamlandı"


def test_run_agent_loop_confirm_required_stops():
    def fake_runner(step: str, idx: int, total: int) -> dict:
        if idx == 1:
            return {"status": "confirm_required", "summary": "onay gerekli"}
        return {"status": "completed", "summary": "ok"}

    out = run_agent_loop("production deploy yap", step_runner=fake_runner, max_steps=3)
    assert out["status"] == "confirm_required"
    assert out["completed_steps"] == 0
    assert len(out["trace"]) == 1
    assert out["final"]["state"] == "yarım kaldı"


def test_run_agent_loop_failed_stops():
    def fake_runner(step: str, idx: int, total: int) -> dict:
        if idx == 2:
            return {"status": "failed", "summary": "adım başarısız"}
        return {"status": "completed", "summary": "ok"}

    out = run_agent_loop("bana bir program yap", step_runner=fake_runner, max_steps=4)
    assert out["status"] == "error"
    assert out["completed_steps"] == 1
    assert len(out["trace"]) == 2
    assert out["final"]["state"] == "yarım kaldı"


def test_wait_for_task_completion_reads_processed_result(tmp_path: Path):
    processed = tmp_path / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    task_id = "TASK-UNIT-1"
    (processed / f"{task_id}.json").write_text('{"task_id":"TASK-UNIT-1","status":"completed"}', encoding="utf-8")

    out = wait_for_task_completion(task_id, processed_dir=str(processed), timeout_seconds=1)
    assert out["status"] == "completed"


def test_run_agent_loop_timeout_retries_then_stops():
    calls = {"n": 0}

    def fake_runner(step: str, idx: int, total: int) -> dict:
        calls["n"] += 1
        return {"status": "timeout", "summary": "iş sonucu bekleniyor"}

    out = run_agent_loop("bana bir program yap", step_runner=fake_runner, max_steps=3, timeout_retries=1)
    assert out["status"] == "error"
    assert out["completed_steps"] == 0
    assert out["trace"][0]["attempts"] == 2
    assert "Retry limiti" in out["trace"][0]["summary"]


def test_build_plan_empty_goal_raises():
    try:
        build_plan("", max_steps=3)
        assert False, "expected ValueError"
    except ValueError as e:
        assert str(e) == "empty_goal"
