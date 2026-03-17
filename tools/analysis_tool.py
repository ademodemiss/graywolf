import argparse
import json
from core.llm_router import LLMRouter


class AnalysisTool:
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
        self.llm = self.llm_router.get()  # RoutedLLMAdapter instance

    @staticmethod
    def _normalize_llm_output(output):
        if isinstance(output, tuple):
            return output[0]
        return output

    def analyze_financial_data(self, ticker: str, data: dict) -> dict:
        """
        Finansal verileri LLM kullanarak analiz eder.
        Veriler genellikle get_stock_data veya get_ticker_info'dan gelir.
        """
        prompt = (
            f"' {ticker}' hisse senedi için aşağıdaki finansal verileri analiz et ve kısa bir özet sun. "
            f"Aşağıdaki soruları yanıtla: Ana trendler nelerdir? Potansiyel riskler var mı? Kısa vadeli tahminin nedir? "
            f"Yanıtını 150 kelimeyi geçmeyecek şekilde sadece Türkçe olarak ver.\n\nVeriler: {json.dumps(data, indent=2)}"
        )

        try:
            analysis_result = self._normalize_llm_output(self.llm.generate_response(prompt))
            return {"status": "ok", "ticker": ticker, "analysis": analysis_result}
        except Exception as e:
            return {"status": "error", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="GrayWolf Finansal Analiz Aracı")
    parser.add_argument("--ticker", required=True, help="Hisse senedi sembolü (örn. 'AAPL')")
    parser.add_argument("--data", required=True, help="Analiz edilecek JSON formatında finansal veri")

    args = parser.parse_args()

    llm_router = LLMRouter()  # Yeni bir LLMRouter örneği oluştur
    tool = AnalysisTool(llm_router)

    try:
        financial_data = json.loads(args.data)
    except json.JSONDecodeError:
        parser.error("--data argümanı geçerli bir JSON formatında olmalı.")

    result = tool.analyze_financial_data(args.ticker, financial_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
