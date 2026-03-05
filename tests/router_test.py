import argparse
import json

from adapters.llm.llm_adapter import LLMAdapter
from core.llm_router import LLMRouter, RateLimitError, RoutedLLMAdapter


class _PrimaryFailAdapter(LLMAdapter):
    def generate_response(self, prompt: str, **kwargs) -> str:
        raise RateLimitError("simulated codex rate limit")

    def get_model_info(self) -> dict:
        return {"name": "codex-sim", "provider": "codex"}

    def stream_response(self, prompt: str, **kwargs):
        raise RateLimitError("simulated codex rate limit")
        yield ""

    def chat_completion(self, messages: list[dict], **kwargs) -> str:
        raise RateLimitError("simulated codex rate limit")


class _FallbackOkAdapter(LLMAdapter):
    def generate_response(self, prompt: str, **kwargs) -> str:
        return "gemini-fallback-ok"

    def get_model_info(self) -> dict:
        return {"name": "gemini-sim", "provider": "gemini"}

    def stream_response(self, prompt: str, **kwargs):
        yield "gemini-fallback-ok"

    def chat_completion(self, messages: list[dict], **kwargs) -> str:
        return "gemini-fallback-ok"


def main():
    parser = argparse.ArgumentParser(description="GrayWolf router test")
    parser.add_argument("--simulate-rate-limit", action="store_true")
    args = parser.parse_args()

    if args.simulate_rate_limit:
        router = RoutedLLMAdapter(
            primary=_PrimaryFailAdapter(),
            fallback=_FallbackOkAdapter(),
            primary_name="codex",
            fallback_name="gemini",
        )
        out = router.generate_response("hello")
        print(json.dumps({"status": "ok", "fallback_to": "gemini", "response": out}, ensure_ascii=False))
        return

    llm = LLMRouter().get()
    out = llm.generate_response("router smoke")
    print(json.dumps({"status": "ok", "response": out}, ensure_ascii=False))


if __name__ == "__main__":
    main()
