import json
from argparse import Namespace

import core.graywolf_cli as cli


def test_cmd_agent_preserves_run_id_and_increments_pause_count_on_second_confirm(monkeypatch):
    saved = []

    def fake_save(_state_dir, _run_id, state):
        saved.append(state)
        return "state.json"

    first_out = {
        "status": "confirm_required",
        "plan": ["s1", "s2"],
        "trace": [{"index": 1, "step": "s1"}],
        "pause": {"step_index": 1, "approval_request_id": "APR-1"},
        "final": {"state": "yarım kaldı", "reason": "Adım 1 onay bekliyor."},
    }

    second_out = {
        "status": "confirm_required",
        "plan": ["s1", "s2", "s3"],
        "trace": [{"index": 1, "step": "s1"}, {"index": 2, "step": "s2"}],
        "pause": {"step_index": 2, "approval_request_id": "APR-2"},
        "final": {"state": "yarım kaldı", "reason": "Adım 2 onay bekliyor."},
    }

    monkeypatch.setattr(cli, "save_agent_state", fake_save)
    monkeypatch.setattr(cli, "run_agent_loop", lambda *args, **kwargs: first_out)

    args1 = Namespace(
        goal="production deploy yap",
        max_steps=4,
        source="graywolf-agent",
        session_id="graywolf-agent",
        plan_only=False,
        resume_run_id="",
    )
    out1 = cli.cmd_agent(args1)
    run_id = out1["run_id"]
    assert out1["continuity"]["pause_count"] == 1
    assert out1["continuity"]["resume_count"] == 0

    resumed_state = {
        "run_id": run_id,
        "goal": "production deploy yap",
        "max_steps": 4,
        "next_step_index": 2,
        "plan": ["s1", "s2", "s3"],
        "trace": [{"index": 1, "step": "s1"}],
        "continuity": out1["continuity"],
    }

    monkeypatch.setattr(cli, "load_agent_state", lambda *_: resumed_state)
    monkeypatch.setattr(cli, "run_agent_loop", lambda *args, **kwargs: second_out)

    args2 = Namespace(
        goal="production deploy yap",
        max_steps=4,
        source="graywolf-agent",
        session_id="graywolf-agent",
        plan_only=False,
        resume_run_id=run_id,
    )
    out2 = cli.cmd_agent(args2)

    assert out2["run_id"] == run_id
    assert out2["continuity"]["pause_count"] == 2
    assert out2["continuity"]["resume_count"] == 1
    assert out2["continuity"]["last_approval_request_id"] == "APR-2"
    assert saved[-1]["continuity"]["pause_count"] == 2


def test_cmd_approve_updates_continuity_and_resumes_same_run(monkeypatch):
    calls = []
    saved = []

    state = {
        "run_id": "ARUN-UNIT-1",
        "goal": "production deploy yap",
        "session_id": "graywolf-agent",
        "source": "graywolf-agent",
        "max_steps": 4,
        "status": "confirm_required",
        "plan": ["s1", "s2"],
        "trace": [{"index": 1, "step": "s1"}],
        "pause": {"step_index": 1, "approval_request_id": "APR-UNIT-1"},
        "continuity": {"run_id": "ARUN-UNIT-1", "pause_count": 1, "resume_count": 0, "approved_request_ids": []},
    }

    def fake_run(cmd):
        calls.append(cmd)
        if "approval-callback" in cmd:
            payload = {"queued": {"task": {"task_id": "TASK-UNIT-1"}}}
            return {"exit_code": 0, "stdout": json.dumps(payload), "stderr": "", "cmd": " ".join(cmd)}
        if cmd and cmd[0].endswith("graywolf") and "agent" in cmd:
            payload = {"status": "confirm_required", "run_id": "ARUN-UNIT-1"}
            return {"exit_code": 0, "stdout": json.dumps(payload), "stderr": "", "cmd": " ".join(cmd)}
        return {"exit_code": 1, "stdout": "", "stderr": "unexpected", "cmd": " ".join(cmd)}

    monkeypatch.setattr(cli, "_run", fake_run)
    monkeypatch.setattr(cli, "find_state_by_request_id", lambda *_: state)
    monkeypatch.setattr(cli, "wait_for_task_completion", lambda *args, **kwargs: {"status": "completed", "summary": "ok"})
    monkeypatch.setattr(cli, "save_agent_state", lambda _d, _r, s: saved.append(s) or "state.json")

    args = Namespace(request_id="APR-UNIT-1", actor="graywolf-cli")
    out = cli.cmd_approve(args)

    assert out["status"] == "ok"
    assert out["run_id"] == "ARUN-UNIT-1"
    assert out["agent_resume"]["run_id"] == "ARUN-UNIT-1"
    assert "APR-UNIT-1" in saved[-1]["continuity"]["approved_request_ids"]

    resume_calls = [c for c in calls if c and c[0].endswith("graywolf") and "agent" in c]
    assert resume_calls, "resume çağrısı bekleniyordu"
    assert "--resume-run-id" in resume_calls[-1]
    assert "ARUN-UNIT-1" in resume_calls[-1]
