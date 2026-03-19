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


def test_explain_error_with_payload_json_hint():
    out = explain_execution({"status": "error", "error": "invalid_payload_json: Expecting value"})
    assert "invalid_payload_json" in out["summary"]
    assert "Payload JSON" in out["next_step"]


def test_explain_error_with_permission_hint():
    out = explain_execution({"status": "error", "errors": ["Permission denied while opening file"]})
    assert "Permission denied" in out["summary"]
    assert "izin" in out["next_step"].lower()
