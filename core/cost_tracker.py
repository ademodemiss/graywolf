import datetime
import json
import os

class CostTracker:
    def __init__(self, log_dir="./logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, "llm_costs.log")

    def log_cost(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int, cost: float, currency: str = "USD"):
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "provider": provider,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cost": cost,
            "currency": currency,
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def calculate_cost(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        # Basit bir maliyet hesaplama örneği. Gerçek maliyetler API'den alınmalı veya konfigüre edilmeli.
        # Bu değerler sadece örnek amaçlıdır.
        cost_per_token = {
            "gemini": {"gemini-2.5-flash": {"input": 0.00000025, "output": 0.00000050}},
            "codex": {"gpt-3.5-turbo": {"input": 0.0000015, "output": 0.000002}},
        }

        provider_costs = cost_per_token.get(provider.lower())
        if not provider_costs:
            return 0.0

        model_costs = provider_costs.get(model.lower())
        if not model_costs:
            return 0.0

        input_cost = prompt_tokens * model_costs["input"]
        output_cost = completion_tokens * model_costs["output"]
        return input_cost + output_cost

if __name__ == "__main__":
    tracker = CostTracker()
    # Örnek kullanım
    provider = "gemini"
    model = "gemini-2.5-flash"
    prompt_tokens = 100
    completion_tokens = 50
    
    cost = tracker.calculate_cost(provider, model, prompt_tokens, completion_tokens)
    tracker.log_cost(provider, model, prompt_tokens, completion_tokens, cost)
    print(f"Logged cost: {cost}")

    provider = "codex"
    model = "gpt-3.5-turbo"
    prompt_tokens = 200
    completion_tokens = 100
    cost = tracker.calculate_cost(provider, model, prompt_tokens, completion_tokens)
    tracker.log_cost(provider, model, prompt_tokens, completion_tokens, cost)
    print(f"Logged cost: {cost}")
