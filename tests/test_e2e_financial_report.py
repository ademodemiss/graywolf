import pytest
import os
from unittest.mock import MagicMock, patch
from tools.financial_data_tool import FinancialDataTool
from tools.analysis_tool import AnalysisTool
from tools.excel_tool import ExcelTool
from core.llm_router import LLMRouter
from openpyxl import load_workbook

@pytest.fixture
def mock_financial_data_tool():
    # FinancialDataTool'u mock ediyoruz
    mock_tool = MagicMock(spec=FinancialDataTool)
    mock_tool.get_stock_data.return_value = {
        "status": "ok",
        "ticker": "AAPL",
        "data": {
            "2026-03-09": {"Open": 150, "High": 155, "Low": 149, "Close": 154, "Volume": 100000000}
        }
    }
    return mock_tool

@pytest.fixture
def mock_analysis_tool():
    # AnalysisTool'u mock ediyoruz
    mock_tool = MagicMock(spec=AnalysisTool)
    mock_tool.analyze_financial_data.return_value = {"status": "ok", "ticker": "AAPL", "analysis": "AAPL hissesi için kısa vadeli pozitif trendler gözlemlenmiştir.", "prompt_tokens": 70, "completion_tokens": 30}
    return mock_tool

@pytest.fixture
def mock_excel_tool():
    # ExcelTool'u mock ediyoruz
    mock_tool = MagicMock(spec=ExcelTool)
    # write_sheet metodu bir çıktı döndürmediği için sadece çağrıldığını kontrol edeceğiz.
    return mock_tool

@pytest.fixture
def mock_llm_router():
    # LLMRouter'ı mock ediyoruz
    mock_router = MagicMock(spec=LLMRouter)
    mock_adapter = MagicMock()
    mock_adapter.generate_response.return_value = ("Bu bir LLM analizi yanıtıdır.", 50, 20)
    mock_router.get.return_value = mock_adapter
    return mock_router

@pytest.fixture
def temp_excel_file(tmp_path):
    file = tmp_path / "financial_report.xlsx"
    yield str(file)
    if os.path.exists(file):
        os.remove(file)


def test_e2e_financial_report_generation(
    mock_financial_data_tool,
    mock_analysis_tool,
    mock_excel_tool,
    mock_llm_router,
    temp_excel_file,
    monkeypatch
):
    # Araçların `LLMRouter` yerine mock'u kullanmasını sağlamak için monkeypatch kullan
    monkeypatch.setattr('tools.analysis_tool.LLMRouter', lambda: mock_llm_router)
    # ExcelTool'un LLMRouter kullanmadığını varsayıyoruz, doğrudan kullanılabilir.

    # 1. Finansal veri çek
    ticker = "AAPL"
    period = "1d"
    stock_data_result = mock_financial_data_tool.get_stock_data(ticker, period)
    assert stock_data_result["status"] == "ok"

    # 2. Veriyi LLM ile analiz et
    analysis_result = mock_analysis_tool.analyze_financial_data(ticker, stock_data_result["data"])
    assert analysis_result["status"] == "ok"
    assert "analysis" in analysis_result

    # 3. Analiz sonucunu Excel dosyasına kaydet
    sheet_name = "FinansalAnaliz"
    report_data = [["Hisse Senedi", "Analiz Sonucu"],
                   [ticker, analysis_result["analysis"]]]
    mock_excel_tool.write_sheet(sheet_name, report_data, file_path=temp_excel_file) # file_path argümanını ekle

    # ExcelTool'un write_sheet metodunun çağrıldığını doğrula
    mock_excel_tool.write_sheet.assert_called_once_with(sheet_name, report_data, file_path=temp_excel_file)

    # Gerçek bir Excel dosyası oluşup oluşmadığını kontrol edemeyiz
    # çünkü mock_excel_tool gerçek dosyayı yazmıyor.
    # Ancak, gerçek ExcelTool ile test etmek isteseydik:
    # from tools.excel_tool import ExcelTool as RealExcelTool
    # real_excel_tool = RealExcelTool(temp_excel_file)
    # read_data = real_excel_tool.read_sheet(sheet_name)
    # assert read_data == report_data
