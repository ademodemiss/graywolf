import argparse
import json
from core.llm_router import LLMRouter

class CodeTool:
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router
        self.llm = self.llm_router.get() # RoutedLLMAdapter instance

    @staticmethod
    def _normalize_llm_output(output):
        if isinstance(output, tuple):
            return output[0]
        return output

    def generate_code(self, requirement: str, language: str = "python") -> dict:
        """
        Belirli bir gereksinime göre kod parçacığı üretir.
        """
        prompt = (
            f"' {language}' dilinde, aşağıdaki gereksinime uygun bir kod parçacığı üret. "
            f"Sadece kodu döndür, açıklama veya ek metin ekleme. "
            f"Gereksinim: {requirement}"
        )
        try:
            code_output = self._normalize_llm_output(self.llm.generate_response(prompt))
            return {"status": "ok", "language": language, "requirement": requirement, "code": code_output}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def analyze_code(self, code: str, analysis_type: str = "explanation") -> dict:
        """
        Verilen kodu analiz eder ve belirli bir analiz türüne göre bilgi sunar.
        analysis_type: 'explanation', 'improvements', 'bugs', 'performance'
        """
        analysis_prompts = {
            "explanation": "Aşağıdaki kodu açıkla.",
            "improvements": "Aşağıdaki kodu iyileştirmek için önerilerde bulun.",
            "bugs": "Aşağıdaki kodda olası hataları veya güvenlik açıklarını bul.",
            "performance": "Aşağıdaki kodun performansını nasıl artırabiliriz?"
        }
        
        if analysis_type not in analysis_prompts:
            return {"status": "error", "error": f"Geçersiz analiz türü: {analysis_type}"}

        prompt = (
            f"Aşağıdaki kodu analiz et ve {analysis_prompts[analysis_type]} "
            f"Yanıtını 200 kelimeyi geçmeyecek şekilde sadece Türkçe olarak ver.\n\nKod:\n```\n{code}\n```"
        )
        try:
            analysis_result = self._normalize_llm_output(self.llm.generate_response(prompt))
            return {"status": "ok", "analysis_type": analysis_type, "analysis": analysis_result}
        except Exception as e:
            return {"status": "error", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="GrayWolf Kod Aracı")
    parser.add_argument("--action", required=True, choices=["generate_code", "analyze_code"], help="Yapılacak eylem")
    parser.add_argument("--requirement", help="Kod üretimi için gereksinim")
    parser.add_argument("--language", default="python", help="Kod üretimi için dil")
    parser.add_argument("--code", help="Analiz edilecek kod")
    parser.add_argument("--analysis_type", default="explanation", choices=["explanation", "improvements", "bugs", "performance"], help="Kod analiz türü")
    
    args = parser.parse_args()

    llm_router = LLMRouter() # Yeni bir LLMRouter örneği oluştur
    tool = CodeTool(llm_router)

    if args.action == "generate_code":
        if not args.requirement:
            parser.error("--requirement argümanı gerekli.")
        result = tool.generate_code(args.requirement, args.language)
        print(json.dumps(result, indent=2))
    elif args.action == "analyze_code":
        if not args.code:
            parser.error("--code argümanı gerekli.")
        result = tool.analyze_code(args.code, args.analysis_type)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
