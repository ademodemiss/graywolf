from agent.simple_agent_loop import build_plan, run_agent_loop


def test_build_plan_returns_3_to_5_steps():
    plan = build_plan("bana bir program yap", max_steps=5)
    assert 3 <= len(plan) <= 5


def test_run_agent_loop_success():
    def fake_runner(step: str, idx: int, total: int) -> dict:
        return {"status": "queued", "step": step, "idx": idx, "total": total}

    out = run_agent_loop("bana bir program yap", step_runner=fake_runner, max_steps=4)
    assert out["status"] == "ok"
    assert out["completed_steps"] == 4
    assert len(out["trace"]) == 4


def test_run_agent_loop_stops_on_error():
    def fake_runner(step: str, idx: int, total: int) -> dict:
        if idx == 2:
            return {"status": "error", "step": step}
        return {"status": "queued", "step": step}

    out = run_agent_loop("bana bir program yap", step_runner=fake_runner, max_steps=4)
    assert out["status"] == "error"
    assert out["completed_steps"] == 1
    assert len(out["trace"]) == 2
