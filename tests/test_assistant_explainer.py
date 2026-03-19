from core.assistant_explainer import explain_execution


def test_explain_queued():
    out = explain_execution({"status": "queued", "intent": "healthcheck", "task_id": "TASK-1"})
    assert "kuyruğa alındı" in out["summary"]
    assert "TASK-1" in out["summary"]


def test_explain_confirm_required():
    out = explain_execution({"status": "confirm_required", "intent": "deploy"})
    assert "onay bekliyor" in out["summary"]
    assert "approvals" in out["next_step"]


def test_explain_denied():
    out = explain_execution({"status": "denied", "intent": "disable_guardrails"})
    assert "reddedildi" in out["summary"]


def test_explain_error():
    out = explain_execution({"status": "error"})
    assert "hata" in out["summary"]
    assert "precheck" in out["next_step"]
