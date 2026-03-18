import pytest
import json
from unittest.mock import MagicMock
from tools.analysis_tool import AnalysisTool
from core.llm_router import LLMRouter # Import the actual LLMRouter

@pytest.fixture
def mock_llm_router():
    mock_router = MagicMock(spec=LLMRouter)
    mock_adapter = MagicMock()
    mock_adapter.generate_response.return_value = ("Bu bir test analizidir.", 50, 20) # (text, prompt_tokens, completion_tokens)
    mock_router.get.return_value = mock_adapter
    return mock_router

def test_analyze_financial_data(mock_llm_router):
    tool = AnalysisTool(llm_router=mock_llm_router)
    ticker = "TEST"
    data = {"price": 100, "volume": 1000}
    result = tool.analyze_financial_data(ticker, data)

    assert result["status"] == "ok"
    assert result["ticker"] == ticker
    assert "analysis" in result
    assert result["analysis"] == "Bu bir test analizidir."

    # LLM'in çağrıldığını ve doğru prompt ile çağrıldığını kontrol et
    mock_llm_router.get.assert_called_once() # LLMRouter.get() çağrıldı mı?
    mock_llm_router.get.return_value.generate_response.assert_called_once() # generate_response çağrıldı mı?
    # generate_response metodunun ilk argümanının bir string olduğunu ve 'TEST' içerdiğini kontrol et
    assert "TEST" in mock_llm_router.get.return_value.generate_response.call_args[0][0]

def test_analyze_financial_data_llm_error(mock_llm_router):
    mock_llm_router.get.return_value.generate_response.side_effect = Exception("LLM Hatası")
    tool = AnalysisTool(llm_router=mock_llm_router)
    ticker = "TESTERR"
    data = {"price": 100}
    result = tool.analyze_financial_data(ticker, data)

    assert result["status"] == "error"
    assert "LLM Hatası" in result["error"]
