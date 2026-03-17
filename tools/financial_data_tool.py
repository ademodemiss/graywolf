import argparse
import yfinance as yf
import pandas as pd
import json
from datetime import datetime, timedelta

class FinancialDataTool:
    def __init__(self):
        pass

    def get_stock_data(self, ticker: str, period: str = "1y", interval: str = "1d") -> dict:
        """
        Belirli bir hisse senedi (ticker) için geçmiş verileri çeker.
        period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
        interval: '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            if hist.empty:
                return {"status": "error", "error": f"' {ticker}' için veri bulunamadı veya geçersiz ticker/dönem."}
            
            # Tarih indeksini formatla ve veri çerçevesini JSON'a dönüştür
            hist.index = hist.index.strftime('%Y-%m-%d %H:%M:%S')
            return {"status": "ok", "ticker": ticker, "data": hist.to_dict(orient='index')}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_ticker_info(self, ticker: str) -> dict:
        """
        Belirli bir hisse senedinin (ticker) temel bilgilerini çeker.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if not isinstance(info, dict) or not info:
                return {"status": "error", "error": f"' {ticker}' için bilgi bulunamadı."}
            # Invalid ticker'larda yfinance bazen sınırlı hata sözlüğü dönebiliyor.
            if not any(k in info for k in ("shortName", "longName", "symbol", "sector")):
                return {"status": "error", "error": f"' {ticker}' için geçerli şirket bilgisi bulunamadı."}
            return {"status": "ok", "ticker": ticker, "info": info}
        except Exception as e:
            return {"status": "error", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="GrayWolf Finansal Veri Aracı")
    parser.add_argument("--action", required=True, choices=["get_stock_data", "get_ticker_info"], help="Yapılacak eylem")
    parser.add_argument("--ticker", required=True, help="Hisse senedi sembolü (örn. 'AAPL', 'MSFT')")
    parser.add_argument("--period", default="1y", help="Veri dönemi (örn. '1d', '1mo', '1y') - get_stock_data için")
    parser.add_argument("--interval", default="1d", help="Veri aralığı (örn. '1m', '1h', '1d') - get_stock_data için")
    
    args = parser.parse_args()

    tool = FinancialDataTool()

    if args.action == "get_stock_data":
        result = tool.get_stock_data(args.ticker, args.period, args.interval)
        print(json.dumps(result, indent=2))
    elif args.action == "get_ticker_info":
        result = tool.get_ticker_info(args.ticker)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
