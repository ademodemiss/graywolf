import pytest
import json
import pandas as pd
from tools.financial_data_tool import FinancialDataTool

# yfinance bağımlılığı nedeniyle gerçek ağ isteklerinden kaçınmak için
# testlerde basitleştirilmiş bir yaklaşım izliyoruz.
# Bu, mock objeleri veya önceden tanımlanmış veri setleri kullanmayı içerebilir.

@pytest.fixture
def financial_tool():
    return FinancialDataTool()

def test_get_stock_data_mock(financial_tool, monkeypatch):
    # yfinance'ın Ticker sınıfını mock ediyoruz
    class MockHistory:
        def __init__(self, ticker):
            self.ticker = ticker
        def history(self, period, interval):
            if self.ticker == "AAPL" and period == "1d":
                # Basit bir örnek veri döndür
                return pd.DataFrame({
                    'Open': [150.0],
                    'High': [155.0],
                    'Low': [149.0],
                    'Close': [154.0],
                    'Volume': [100000000]
                }, index=pd.to_datetime(['2026-03-09']))
            return pd.DataFrame() # Boş dataframe

    class MockTicker:
        def __init__(self, ticker):
            self.ticker = ticker
        def history(self, period, interval):
            return MockHistory(self.ticker).history(period, interval)

    monkeypatch.setattr('yfinance.Ticker', MockTicker)

    result = financial_tool.get_stock_data("AAPL", period="1d")
    assert result["status"] == "ok"
    assert result["ticker"] == "AAPL"
    assert "data" in result
    assert len(result["data"]) > 0

def test_get_ticker_info_mock(financial_tool, monkeypatch):
    # yfinance'ın Ticker sınıfını mock ediyoruz
    class MockInfo:
        def __init__(self, ticker):
            self.ticker = ticker
            self.info = {"shortName": "Apple Inc.", "sector": "Technology"} if ticker == "AAPL" else {}

    class MockTicker:
        def __init__(self, ticker):
            self.ticker = ticker
            self.info = MockInfo(ticker).info

    monkeypatch.setattr('yfinance.Ticker', MockTicker)

    result = financial_tool.get_ticker_info("AAPL")
    assert result["status"] == "ok"
    assert result["ticker"] == "AAPL"
    assert "info" in result
    assert result["info"]["shortName"] == "Apple Inc."

def test_get_stock_data_invalid_ticker(financial_tool):
    result = financial_tool.get_stock_data("INVALIDTICKER")
    assert result["status"] == "error"

def test_get_ticker_info_invalid_ticker(financial_tool):
    result = financial_tool.get_ticker_info("INVALIDTICKER")
    assert result["status"] == "error"
