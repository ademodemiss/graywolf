"""Gerçek LLM çağrılarına geçiş için iskelet ve token/cost alanı."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from adapters.llm.token_estimator import estimate_usage
from core.cost_tracker import CostTracker


@dataclass
class RealLLMResponse:
    model: str
    prompt: str
    response: str
    usage: Mapping[str, int]
    estimated_cost: float


class RealLLMClient:
    def __init__(
        self,
        model: str = "gemini-pro",
        provider: str = "gemini",
        cost_tracker: CostTracker | None = None,
    ) -> None:
        self.provider = provider
        self.model = model
        self.cost_tracker = cost_tracker or CostTracker()

    def generate(self, prompt: str) -> RealLLMResponse:
        response = self._simulate_response(prompt)
        usage = estimate_usage(prompt, response)
        cost = self.cost_tracker.calculate_cost(
            self.provider,
            self.model,
            usage["prompt_tokens"],
            usage["response_tokens"],
        )
        rounded_cost = round(cost, 8)
        self.cost_tracker.log_cost(
            self.provider,
            self.model,
            usage["prompt_tokens"],
            usage["response_tokens"],
            rounded_cost,
        )
        return RealLLMResponse(
            model=self.model,
            prompt=prompt,
            response=response,
            usage=usage,
            estimated_cost=rounded_cost,
        )

    def _simulate_response(self, prompt: str) -> str:
        return f"[simulated {self.model} response] {prompt[:200]}"
