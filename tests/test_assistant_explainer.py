from core.assistant_explainer import explain_execution, score_ux_output


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


def test_score_ux_output_good():
    ux = {
        "summary": "İş kuyruğa alındı. Intent: healthcheck.",
        "next_step": "`graywolf queue --limit 5` ile takip edebilirsin.",
    }
    q = score_ux_output(ux)
    assert q["score"] == 3
    assert q["level"] == "good"
    assert q["checks"]["summary_clear"] is True
    assert q["checks"]["next_step_actionable"] is True


def test_score_ux_output_detects_filler():
    ux = {
        "summary": "Harika soru, yardımcı olmaktan mutluluk duyarım.",
        "next_step": "Bakabiliriz.",
    }
    q = score_ux_output(ux)
    assert q["checks"]["has_filler"] is True
    assert q["score"] <= 2
