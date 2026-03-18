import os
import pytest
import json
from unittest.mock import MagicMock
from tools.self_improve_tool import SelfImproveTool
from core.llm_router import LLMRouter

@pytest.fixture
def mock_llm_router_for_self_improve():
    mock_router = MagicMock(spec=LLMRouter)
    mock_adapter = MagicMock()
    mock_adapter.generate_response.return_value = "Geliştirme önerileri: Logları daha sık kontrol edin."
    mock_router.get.return_value = mock_adapter
    return mock_router

@pytest.fixture
def temp_log_file(tmp_path):
    log_file = tmp_path / "terminal.log"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(json.dumps({"ts": "2026-03-09T10:00:00Z", "cmd": "ls /no_such_dir", "decision": "deny", "reason": "policy", "status": "blocked"}) + "\n")
        f.write(json.dumps({"ts": "2026-03-09T10:01:00Z", "cmd": "python script.py", "decision": "allow", "status": "error", "stderr": "FileNotFound"}) + "\n")
        f.write(json.dumps({"ts": "2026-03-09T10:02:00Z", "cmd": "echo hello", "decision": "allow", "status": "success"}) + "\n")
        f.write(json.dumps({"ts": "2026-03-09T10:03:00Z", "cmd": "rm /important_file", "decision": "needs_confirmation", "status": "needs_confirmation"}) + "\n")
    yield str(log_file)
    if os.path.exists(log_file):
        os.remove(log_file)

def test_analyze_logs_for_improvements(mock_llm_router_for_self_improve):
    tool = SelfImproveTool(llm_router=mock_llm_router_for_self_improve)
    log_content = "Terminal log content here."
    context = "Agent performansı"
    result = tool.analyze_logs_for_improvements(log_content, context)

    assert result["status"] == "ok"
    assert result["analysis"] == "Geliştirme önerileri: Logları daha sık kontrol edin."
    mock_llm_router_for_self_improve.get.return_value.generate_response.assert_called_once()
    assert "Terminal log content here." in mock_llm_router_for_self_improve.get.return_value.generate_response.call_args[0][0]
    assert "Agent performansı" in mock_llm_router_for_self_improve.get.return_value.generate_response.call_args[0][0]

def test_get_past_errors_summary(temp_log_file, mock_llm_router_for_self_improve):
    tool = SelfImproveTool(llm_router=mock_llm_router_for_self_improve)
    result = tool.get_past_errors_summary(error_logs_path=temp_log_file, num_errors=2)

    assert result["status"] == "ok"
    assert len(result["errors"]) == 2
    assert result["errors"][0]["decision"] == "needs_confirmation"
    assert result["errors"][1]["status"] == "error"


def test_get_past_errors_summary_no_file(mock_llm_router_for_self_improve):
    tool = SelfImproveTool(llm_router=mock_llm_router_for_self_improve)
    result = tool.get_past_errors_summary(error_logs_path="/non/existent/path/log.log")
    assert result["status"] == "warning"
    assert "Log dosyası bulunamadı" in result["message"]
    assert result["errors"] == []


def test_analyze_logs_includes_replan_summary(mock_llm_router_for_self_improve):
    tool = SelfImproveTool(llm_router=mock_llm_router_for_self_improve)
    replan_summary = "Replan hazır: workflow=orchestrator-plan hint=adjust_permissions"
    tool.analyze_logs_for_improvements("log içeriği", "önemli", replan_summary)

    prompt = mock_llm_router_for_self_improve.get.return_value.generate_response.call_args[0][0]
    assert "Replan özeti" in prompt
    assert replan_summary in prompt


def test_summarize_replan_events(tmp_path, mock_llm_router_for_self_improve):
    log_file = tmp_path / "replan.log"
    entries = [
        {
            "stage": "ready",
            "payload": {
                "workflow_name": "orchestrator-plan",
                "hint": "adjust_permissions",
                "original_error": {"stderr_snippet": "perm"},
            },
        },
        {
            "stage": "executed",
            "payload": {
                "workflow_name": "orchestrator-plan",
                "replan_result": {
                    "status": "completed",
                    "results": [
                        {"name": "replan_inspect", "status": "success"},
                    ],
                },
            },
        },
    ]
    with open(log_file, "w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    tool = SelfImproveTool(llm_router=mock_llm_router_for_self_improve)
    summary = tool.summarize_replan_events(str(log_file), limit=2)

    assert "workflow=orchestrator-plan" in summary
    assert "[Hazır]" in summary or "[Tamamlandı]" in summary


def test_improve_from_replan_entries_filters_granted(mock_llm_router_for_self_improve):
    tool = SelfImproveTool(llm_router=mock_llm_router_for_self_improve)
    entries = [
        {
            "event": "REPLAN_READY",
            "ts": "2026-03-11T12:00:00+00:00",
            "payload": {"workflow_name": "orchestrator-plan", "hint": "adjust_permissions"},
            "analysis": {"status": "ok", "summary": "adjust permissions"},
            "approval_request": {"status": "GRANTED", "request_id": "req-1", "granted_at": "2026-03-11T12:01:00+00:00"},
        },
        {
            "event": "REPLAN_READY",
            "ts": "2026-03-11T12:05:00+00:00",
            "payload": {"workflow_name": "orchestrator-plan"},
            "analysis": {"status": "error"},
            "approval_request": {"status": "PENDING", "request_id": "req-2"},
        },
    ]

    jobs = tool.improve_from_replan_entries(entries)

    assert len(jobs) == 1
    job = jobs[0]
    assert job["request_id"] == "req-1"
    assert job["workflow"] == "orchestrator-plan"
    assert job["analysis_status"] == "ok"
    assert job["analysis_summary"] == "adjust permissions"
    assert job["replan_reason"] == "adjust_permissions"
    assert job["approved_at"] == "2026-03-11T12:01:00+00:00"


def test_improve_from_replan_entries_respects_limit(mock_llm_router_for_self_improve):
    tool = SelfImproveTool(llm_router=mock_llm_router_for_self_improve)
    entries = [
        {
            "event": "REPLAN_READY",
            "ts": "2026-03-11T12:00:00+00:00",
            "payload": {"workflow": "phase265", "hint": "retry"},
            "analysis": {"status": "ok"},
            "approval_request": {"status": "GRANTED", "request_id": f"req-{i}"},
        }
        for i in range(5)
    ]

    jobs = tool.improve_from_replan_entries(entries, limit=3)
    assert len(jobs) == 3
