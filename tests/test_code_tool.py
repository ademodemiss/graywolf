import pytest
import json
from unittest.mock import MagicMock
from tools.code_tool import CodeTool
from core.llm_router import LLMRouter

@pytest.fixture
def mock_llm_router_for_code_tool():
    mock_router = MagicMock(spec=LLMRouter)
    mock_adapter = MagicMock()
    mock_adapter.generate_response.return_value = ("print(\"Hello, World!\")", 50, 20) # (text, prompt_tokens, completion_tokens)
    mock_router.get.return_value = mock_adapter
    return mock_router

def test_generate_code(mock_llm_router_for_code_tool):
    tool = CodeTool(llm_router=mock_llm_router_for_code_tool)
    requirement = "Hello World yazan Python kodu"
    result = tool.generate_code(requirement, language="python")

    assert result["status"] == "ok"
    assert result["code"] == "print(\"Hello, World!\")"
    mock_llm_router_for_code_tool.get.return_value.generate_response.assert_called_once()
    assert "Hello World" in mock_llm_router_for_code_tool.get.return_value.generate_response.call_args[0][0]

def test_analyze_code_explanation(mock_llm_router_for_code_tool):
    tool = CodeTool(llm_router=mock_llm_router_for_code_tool)
    code_to_analyze = "def func(): return 1"
    analysis_type = "explanation"
    # Mock LLM response for analysis
    mock_llm_router_for_code_tool.get.return_value.generate_response.return_value = ("Bu kod bir fonksiyon tanımlar.", 50, 20)

    result = tool.analyze_code(code_to_analyze, analysis_type=analysis_type)
    assert result["status"] == "ok"
    assert result["analysis"] == "Bu kod bir fonksiyon tanımlar."
    assert "Aşağıdaki kodu açıkla." in mock_llm_router_for_code_tool.get.return_value.generate_response.call_args[0][0]

def test_analyze_code_invalid_type(mock_llm_router_for_code_tool):
    tool = CodeTool(llm_router=mock_llm_router_for_code_tool)
    code_to_analyze = "some_code"
    analysis_type = "invalid_type"
    result = tool.analyze_code(code_to_analyze, analysis_type=analysis_type)
    assert result["status"] == "error"
    assert "Geçersiz analiz türü" in result["error"]

