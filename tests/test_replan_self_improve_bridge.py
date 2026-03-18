import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from core.approval import ApprovalRequest, ApprovalState
from core.event_bus import EventBus
from core.event_types import EventTypes
from monitor.replan_self_improve_bridge import ReplanSelfImproveBridge


@patch("monitor.replan_self_improve_bridge.send_telegram_message")
def test_replan_ready_triggers_analysis_and_telegram(mock_send, tmp_path):
    bus = EventBus()
    mock_tool = MagicMock()
    mock_tool.summarize_replan_events.return_value = "[Hazır] workflow=orchestrator-plan"
    mock_tool.analyze_logs_for_improvements.return_value = {"status": "ok", "analysis": "Loglar temiz.", "analysis_tokens": 0}

    approval_request = ApprovalRequest(
        request_id="req-123",
        command="replan orchestrator-plan",
        category="replan",
    )
    approval_request.status = ApprovalState.PENDING

    mock_approval_manager = MagicMock()
    mock_approval_manager.evaluate_command.return_value = (approval_request, "onay gerekli")

    log_dir = tmp_path / "logs"
    replan_log = tmp_path / "replan.log"
    bridge = ReplanSelfImproveBridge(
        bus=bus,
        log_dir=str(log_dir),
        replan_log_path=str(replan_log),
        tool=mock_tool,
        approval_manager=mock_approval_manager,
    )

    payload = {"workflow_name": "orchestrator-plan", "hint": "retry"}
    bus.publish(EventTypes.REPLAN_READY, payload)

    mock_tool.summarize_replan_events.assert_called_once_with(str(replan_log))
    mock_tool.analyze_logs_for_improvements.assert_called_once()
    mock_send.assert_called_once()
    mock_approval_manager.evaluate_command.assert_called_once()

    message_text = mock_send.call_args[0][0]
    assert "SelfImprove önerisi" in message_text
    assert "Loglar temiz" in message_text
    assert "Approval talebi: req-123" in message_text

    log_path = log_dir / "self_improve_replan.log"
    assert log_path.exists()
    entry = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])
    assert entry["event"] == EventTypes.REPLAN_READY
    assert entry["approval_request"]["request_id"] == "req-123"


@patch("monitor.replan_self_improve_bridge.send_telegram_message")
def test_replan_executed_handles_analysis_error(mock_send, tmp_path):
    bus = EventBus()
    mock_tool = MagicMock()
    mock_tool.summarize_replan_events.return_value = ""
    mock_tool.analyze_logs_for_improvements.return_value = {"status": "error", "error": "llm down"}

    mock_approval_manager = MagicMock()

    log_dir = tmp_path / "logs"
    bridge = ReplanSelfImproveBridge(
        bus=bus,
        log_dir=str(log_dir),
        replan_log_path=str(tmp_path / "replan.log"),
        tool=mock_tool,
        approval_manager=mock_approval_manager,
    )

    payload = {"workflow_name": "retry-flow"}
    bus.publish(EventTypes.REPLAN_EXECUTED, payload)

    mock_send.assert_called_once()
    mock_approval_manager.evaluate_command.assert_not_called()
    assert "Analiz durumu: error" in mock_send.call_args[0][0]
    assert "Hata: llm down" in mock_send.call_args[0][0]
