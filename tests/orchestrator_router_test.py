import json

from adapters.llm.llm_adapter import LLMAdapter
from core.llm_router import RateLimitError, RoutedLLMAdapter
from core.orchestrator import Orchestrator


class _PrimaryFail(LLMAdapter):
    def generate_response(self, prompt: str, **kwargs) -> str:
        raise RateLimitError("simulated primary failure")

    def get_model_info(self) -> dict:
        return {"name": "codex-sim"}

    def stream_response(self, prompt: str, **kwargs):
        raise RateLimitError("simulated primary failure")
        yield ""

    def chat_completion(self, messages: list[dict], **kwargs) -> str:
        raise RateLimitError("simulated primary failure")


class _FallbackPlan(LLMAdapter):
    def generate_response(self, prompt: str, **kwargs) -> str:
        return "s1|python3 -c \"print('router-ok')\""

    def get_model_info(self) -> dict:
        return {"name": "gemini-sim"}

    def stream_response(self, prompt: str, **kwargs):
        yield "s1|python3 -c \"print('router-ok')\""

    def chat_completion(self, messages: list[dict], **kwargs) -> str:
        return "s1|python3 -c \"print('router-ok')\""


if __name__ == "__main__":
    routed = RoutedLLMAdapter(_PrimaryFail(), _FallbackPlan(), "codex", "gemini")
    orch = Orchestrator(routed)
    planned = orch.plan("router integration")
    execution = orch.execute_plan(planned)
    print(
        json.dumps(
            {
                "planned": [s.__dict__ for s in planned],
                "evaluation": orch.evaluate(execution),
                "execution_status": execution.get("status"),
            },
            ensure_ascii=False,
        )
    )
