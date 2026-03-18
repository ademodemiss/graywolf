import argparse
import json
import re
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf


class FinancialDataTool:
    ALLOWED_PERIODS = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
    ALLOWED_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"}

    def __init__(self):
        pass

    @staticmethod
    def _validate_ticker(ticker: str) -> bool:
        if not ticker:
            return False
        return bool(re.fullmatch(r"[A-Za-z0-9.\-]{1,12}", ticker.strip()))

    @staticmethod
    def _safe_float(v):
        try:
            return float(v)
        except Exception:
            return None

    def get_stock_data(self, ticker: str, period: str = "1y", interval: str = "1d") -> dict:
        """
        Belirli bir hisse senedi (ticker) için geçmiş verileri çeker.
        Hardening: parametre doğrulama + veri kalite özeti + stale veri uyarısı.
        """
        ticker = (ticker or "").strip().upper()
        if not self._validate_ticker(ticker):
            return {"status": "error", "error": "Geçersiz ticker formatı."}
        if period not in self.ALLOWED_PERIODS:
            return {"status": "error", "error": f"Geçersiz period: {period}"}
        if interval not in self.ALLOWED_INTERVALS:
            return {"status": "error", "error": f"Geçersiz interval: {interval}"}

        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            if hist.empty:
                return {"status": "error", "error": f"'{ticker}' için veri bulunamadı veya geçersiz ticker/dönem."}

            if len(hist) > 1000:
                hist = hist.tail(1000)

            hist_clean = hist.copy()
            hist_clean.index = pd.to_datetime(hist_clean.index, utc=True, errors="coerce")
            hist_clean = hist_clean[~hist_clean.index.isna()]
            if hist_clean.empty:
                return {"status": "error", "error": "Tarih indeksi işlenemedi."}

            latest_ts = hist_clean.index.max().to_pydatetime()
            now_utc = datetime.now(timezone.utc)
            stale_days = (now_utc - latest_ts).days if latest_ts else None

            required_cols = ["Open", "High", "Low", "Close", "Volume"]
            present = [c for c in required_cols if c in hist_clean.columns]
            completeness = round(len(present) / len(required_cols) * 100, 1)

            hist_for_json = hist_clean.copy()
            hist_for_json.index = hist_for_json.index.strftime('%Y-%m-%d %H:%M:%S')

            quality_score = 60
            if completeness >= 100:
                quality_score += 20
            if stale_days is not None and stale_days <= 5:
                quality_score += 20

            return {
                "status": "ok",
                "ticker": ticker,
                "data": hist_for_json.to_dict(orient='index'),
                "meta": {
                    "period": period,
                    "interval": interval,
                    "rows": int(len(hist_for_json)),
                    "latest_ts_utc": latest_ts.isoformat() if latest_ts else None,
                    "stale_days": stale_days,
                    "completeness_pct": completeness,
                    "quality_score": int(min(quality_score, 100)),
                    "manual_review_required": True,
                },
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_ticker_info(self, ticker: str) -> dict:
        """
        Belirli bir hisse senedinin (ticker) temel bilgilerini çeker.
        """
        ticker = (ticker or "").strip().upper()
        if not self._validate_ticker(ticker):
            return {"status": "error", "error": "Geçersiz ticker formatı."}
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if not isinstance(info, dict) or not info:
                return {"status": "error", "error": f"'{ticker}' için bilgi bulunamadı."}
            if not any(k in info for k in ("shortName", "longName", "symbol", "sector")):
                return {"status": "error", "error": f"'{ticker}' için geçerli şirket bilgisi bulunamadı."}

            sanitized = {
                "shortName": info.get("shortName"),
                "longName": info.get("longName"),
                "symbol": info.get("symbol") or ticker,
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "marketCap": self._safe_float(info.get("marketCap")),
                "trailingPE": self._safe_float(info.get("trailingPE")),
                "beta": self._safe_float(info.get("beta")),
            }

            return {
                "status": "ok",
                "ticker": ticker,
                "info": sanitized,
                "meta": {
                    "manual_review_required": True,
                    "source": "yfinance",
                },
            }
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
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.action == "get_ticker_info":
        result = tool.get_ticker_info(args.ticker)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
