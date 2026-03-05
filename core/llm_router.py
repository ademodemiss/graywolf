import argparse
from dataclasses import dataclass

from adapters.llm.llm_adapter import LLMAdapter
from core.llm_factory import create_llm


class RateLimitError(Exception):
    pass


class ProviderError(Exception):
    pass


@dataclass
class RouterConfig:
    primary: str = "codex"
    fallback: str = "gemini"


class RoutedLLMAdapter(LLMAdapter):
    RETRYABLE_ERRORS = (RateLimitError, TimeoutError, ConnectionError, ProviderError)

    def __init__(self, primary: LLMAdapter, fallback: LLMAdapter, primary_name: str, fallback_name: str):
        self.primary = primary
        self.fallback = fallback
        self.primary_name = primary_name
        self.fallback_name = fallback_name

    def _normalize_error(self, err: Exception) -> Exception:
        if isinstance(err, self.RETRYABLE_ERRORS):
            return err

        text = str(err).lower()
        if "rate" in text or "429" in text or "quota" in text or "too many" in text:
            return RateLimitError(str(err))
        if "timeout" in text or "timed out" in text:
            return TimeoutError(str(err))
        if "connection" in text or "network" in text or "dns" in text:
            return ConnectionError(str(err))
        return ProviderError(str(err))

    def _fallback_log(self, reason: Exception):
        print(
            f"LLM_ROUTER_FALLBACK primary={self.primary_name} fallback={self.fallback_name} reason={reason.__class__.__name__}:{reason}"
        )

    def _with_fallback(self, fn_name: str, *args, **kwargs):
        try:
            fn = getattr(self.primary, fn_name)
            return fn(*args, **kwargs)
        except Exception as err:
            normalized = self._normalize_error(err)
            if isinstance(normalized, self.RETRYABLE_ERRORS):
                self._fallback_log(normalized)
                fn = getattr(self.fallback, fn_name)
                return fn(*args, **kwargs)
            raise

    def generate_response(self, prompt: str, **kwargs) -> str:
        return self._with_fallback("generate_response", prompt, **kwargs)

    def get_model_info(self) -> dict:
        primary_info = self.primary.get_model_info()
        fallback_info = self.fallback.get_model_info()
        return {"router": "primary_fallback", "primary": primary_info, "fallback": fallback_info}

    def stream_response(self, prompt: str, **kwargs):
        result = self._with_fallback("stream_response", prompt, **kwargs)
        for chunk in result:
            yield chunk

    def chat_completion(self, messages: list[dict], **kwargs) -> str:
        return self._with_fallback("chat_completion", messages, **kwargs)


class LLMRouter:
    def __init__(self, config: RouterConfig | None = None):
        self.config = config or RouterConfig()

    def get(self) -> LLMAdapter:
        primary = create_llm(self.config.primary)
        fallback = create_llm(self.config.fallback)
        return RoutedLLMAdapter(primary, fallback, self.config.primary, self.config.fallback)


def main():
    parser = argparse.ArgumentParser(description="GrayWolf LLM Router")
    parser.add_argument("--prompt", default="Router smoke test")
    args = parser.parse_args()

    llm = LLMRouter().get()
    print(llm.generate_response(args.prompt))


if __name__ == "__main__":
    main()
