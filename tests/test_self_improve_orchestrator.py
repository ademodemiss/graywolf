import pytest
import os
import json
from unittest.mock import MagicMock, patch, mock_open
from core.orchestrator import Orchestrator, OrchestratorStep
from core.llm_router import LLMRouter

@pytest.fixture
def mock_llm_router_for_orchestrator():
    mock_router = MagicMock(spec=LLMRouter)
    mock_adapter = MagicMock()
    mock_adapter.generate_response.return_value = ("task1|echo \"Geliştirme Görevi 1\"\ntask2|echo \"Geliştirme Görevi 2\"", 80, 40) # (text, prompt_tokens, completion_tokens)
    mock_router.get.return_value = mock_adapter
    return mock_router

@pytest.fixture
def temp_self_improve_log(tmp_path):
    log_file = tmp_path / "self_improve_reports.log"
    yield str(log_file)
    if os.path.exists(log_file):
        os.remove(log_file)

@patch('core.orchestrator.run_workflow')
def test_run_self_improve_workflow(
    mock_run_workflow,
    mock_llm_router_for_orchestrator,
    temp_self_improve_log,
    monkeypatch
):
    # Mock workflow çalıştırma sonucu
    mock_run_workflow.return_value = {
        "status": "success",
        "results": [
            {"name": "analyze_logs_with_llm", "status": "success", "stdout": "Örnek performans analizi raporu.\n"}
        ]
    }

    # Orchestrator'ı LLMRouter mock'u ile başlat
    orch = Orchestrator(llm=mock_llm_router_for_orchestrator.get())
    
    # run_self_improve metodunu çağır
    result = orch.run_self_improve(log_path=temp_self_improve_log)

    assert result["status"] == "ok"
    assert "new_steps" in result
    assert len(result["new_steps"]) == 2
    assert result["new_steps"][0]["name"] == "task1"
    assert result["new_steps"][0]["instruction"] == 'echo "Geliştirme Görevi 1"'

    mock_run_workflow.assert_called_once_with({
        'name': 'self-improve-log-analysis',
        'description': 'GrayWolf terminal loglarını analiz eder, hataları tespit eder ve iyileştirme önerileri sunar.',
        'steps': [
            {
                'name': 'analyze_logs_with_llm',
                'cmd': 'python3 tools/self_improve_tool.py --action analyze_logs --log_path /home/adem/graywolf/logs/terminal.log --context "GrayWolf terminal loglarının analizi. Performans iyileştirmeleri, onay/replan olayları ve hataları azaltma hedefleniyor." --include_replan --replan_log_path /home/adem/graywolf/logs/replan_notifier.log --report_path /home/adem/graywolf/logs/self_improve_reports.log'
            }
        ]
    })
    # LLM'e iki kez çağrı yapıldığını doğrula (log analizi ve görev planlama)
    assert mock_llm_router_for_orchestrator.get.return_value.generate_response.call_count == 1 # Tek çağrı bekliyoruz


@patch('core.orchestrator.run_workflow')
def test_run_self_improve_workflow_failure(
    mock_run_workflow,
    mock_llm_router_for_orchestrator,
    temp_self_improve_log,
    monkeypatch
):
    # Workflow başarısız olursa
    mock_run_workflow.return_value = {"status": "error", "error": "Workflow Hatası"}

    orch = Orchestrator(llm=mock_llm_router_for_orchestrator.get())
    result = orch.run_self_improve(log_path=temp_self_improve_log)

    assert result["status"] == "error"
    assert "Self-improve workflow failed" in result["error"]
    mock_run_workflow.assert_called_once_with({
        'name': 'self-improve-log-analysis',
        'description': 'GrayWolf terminal loglarını analiz eder, hataları tespit eder ve iyileştirme önerileri sunar.',
        'steps': [
            {
                'name': 'analyze_logs_with_llm',
                'cmd': 'python3 tools/self_improve_tool.py --action analyze_logs --log_path /home/adem/graywolf/logs/terminal.log --context "GrayWolf terminal loglarının analizi. Performans iyileştirmeleri, onay/replan olayları ve hataları azaltma hedefleniyor." --include_replan --replan_log_path /home/adem/graywolf/logs/replan_notifier.log --report_path /home/adem/graywolf/logs/self_improve_reports.log'
            }
        ]
    })
    mock_llm_router_for_orchestrator.get.return_value.generate_response.assert_not_called()
