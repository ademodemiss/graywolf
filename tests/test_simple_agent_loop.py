from pathlib import Path

from agent.simple_agent_loop import (
    build_plan,
    find_state_by_request_id,
    load_agent_state,
    run_agent_loop,
    save_agent_state,
    wait_for_task_completion,
)


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
    assert out["final"]["classification"] == "completed"
    assert out["trace"][0]["final_reason"] == "completed"


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
    assert out["final"]["classification"] == "blocked"


def test_run_agent_loop_failed_can_skip_and_continue():
    def fake_runner(step: str, idx: int, total: int) -> dict:
        if idx == 2:
            return {"status": "failed", "summary": "adım başarısız"}
        return {"status": "completed", "summary": "ok"}

    out = run_agent_loop("bana bir program yap", step_runner=fake_runner, max_steps=4)
    assert out["status"] == "ok"
    assert len(out["trace"]) >= 3
    assert out["trace"][1]["recovery_strategy"] in {"skip_step", "fallback_step", "alternative_step"}
    assert out["trace"][1]["recovery_attempt"] >= 1


def test_wait_for_task_completion_reads_processed_result(tmp_path: Path):
    processed = tmp_path / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    task_id = "TASK-UNIT-1"
    (processed / f"{task_id}.json").write_text('{"task_id":"TASK-UNIT-1","status":"completed"}', encoding="utf-8")

    out = wait_for_task_completion(task_id, processed_dir=str(processed), timeout_seconds=1)
    assert out["status"] == "completed"


def test_run_agent_loop_timeout_retries_then_recovers_with_skip():
    calls = {"n": 0}

    def fake_runner(step: str, idx: int, total: int) -> dict:
        calls["n"] += 1
        if idx == 1:
            return {"status": "timeout", "summary": "iş sonucu bekleniyor"}
        return {"status": "completed", "summary": "ok"}

    out = run_agent_loop("bana bir program yap", step_runner=fake_runner, max_steps=3, timeout_retries=1)
    assert out["status"] == "ok"
    assert out["trace"][0]["attempts"] == 2
    assert out["trace"][0]["recovery_strategy"] in {"skip_step", "fallback_step"}


def test_build_plan_empty_goal_raises():
    try:
        build_plan("", max_steps=3)
        assert False, "expected ValueError"
    except ValueError as e:
        assert str(e) == "empty_goal"


def test_run_agent_loop_confirm_saves_pause_info():
    def fake_runner(step: str, idx: int, total: int) -> dict:
        return {
            "status": "confirm_required",
            "summary": "onay gerekiyor",
            "approval_request_id": "APR-UNIT-1",
        }

    out = run_agent_loop("deploy yap", step_runner=fake_runner, max_steps=3)
    assert out["status"] == "confirm_required"
    assert out["pause"]["approval_request_id"] == "APR-UNIT-1"
    assert out["pause"]["step_index"] == 1


def test_agent_state_save_load_and_find(tmp_path: Path):
    state_dir = tmp_path / "agent_runs"
    state = {
        "run_id": "ARUN-1",
        "status": "confirm_required",
        "pause": {"approval_request_id": "APR-UNIT-2", "step_index": 2},
        "trace": [],
    }
    save_agent_state(str(state_dir), "ARUN-1", state)
    loaded = load_agent_state(str(state_dir), "ARUN-1")
    found = find_state_by_request_id(str(state_dir), "APR-UNIT-2")
    assert loaded and loaded["run_id"] == "ARUN-1"
    assert found and found["run_id"] == "ARUN-1"


def test_run_agent_loop_resume_from_next_step():
    plan = build_plan("bana bir program yap", max_steps=3)
    existing_trace = [{"index": 1, "step": plan[0], "summary": "step1 done"}]

    def fake_runner(step: str, idx: int, total: int) -> dict:
        return {"status": "completed", "summary": f"step {idx} tamamlandı"}

    out = run_agent_loop(
        "bana bir program yap",
        step_runner=fake_runner,
        max_steps=3,
        start_index=2,
        existing_plan=plan,
        existing_trace=existing_trace,
    )
    assert out["status"] == "ok"
    assert len(out["trace"]) == 3
    assert out["trace"][1]["index"] == 2


def test_run_agent_loop_blocked_uses_adaptive_replan_then_stops():
    def fake_runner(step: str, idx: int, total: int) -> dict:
        if "alternatif yaklaşım" in step.lower():
            return {"status": "blocked", "summary": "alternatif de bloklandı"}
        if "fallback" in step.lower():
            return {"status": "blocked", "summary": "fallback da bloklandı"}
        if "deploy" in step.lower():
            return {"status": "blocked", "summary": "deploy bloklandı"}
        return {"status": "completed", "summary": "ok"}

    out = run_agent_loop("production deploy yap", step_runner=fake_runner, max_steps=3)
    assert out["status"] == "error"
    assert any(t.get("replanned") for t in out["trace"])
    assert any(t.get("alternatives_tried") for t in out["trace"])
    assert out["trace"][0]["replan_depth"] <= 1


def test_run_agent_loop_failed_tries_two_recovery_strategies_when_needed():
    def fake_runner(step: str, idx: int, total: int) -> dict:
        if "alternatif yaklaşım" in step.lower():
            return {"status": "failed", "summary": "alternatif başarısız"}
        if idx == 1:
            return {"status": "failed", "summary": "ilk adım başarısız"}
        return {"status": "completed", "summary": "ok"}

    out = run_agent_loop("sistemde sağlık kontrolü yap", step_runner=fake_runner, max_steps=3)
    assert out["status"] == "ok"
    first = out["trace"][0]
    assert first["replan_depth"] == 1
    assert "alternative_step" in first["alternatives_tried"]
    assert first["recovery_attempt"] == 2
    assert first["recovery_strategy"] == "skip_step"


def test_run_agent_loop_completion_step_marks_partial_completion():
    def fake_runner(step: str, idx: int, total: int) -> dict:
        s = step.lower()
        if "güvenli completion adımı" in s:
            return {"status": "completed", "summary": "completion check başarılı"}
        if "alternatif yaklaşım" in s or "fallback" in s:
            return {"status": "failed", "summary": "recovery başarısız"}
        if idx == total:
            return {"status": "failed", "summary": "son adım başarısız"}
        return {"status": "completed", "summary": "ok"}

    out = run_agent_loop("production deploy yap", step_runner=fake_runner, max_steps=3)
    assert out["status"] == "ok"
    assert out["final"]["classification"] == "partially_completed"
    assert any(t.get("recovery_strategy") == "completion_step" for t in out["trace"])
