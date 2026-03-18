import unittest
from unittest.mock import MagicMock

from adapters.llm import RealLLMClient, estimate_basic_tokens, estimate_usage
from core.cost_tracker import CostTracker


class TokenEstimatorTests(unittest.TestCase):
    def test_estimate_basic_tokens_empty(self):
        self.assertEqual(estimate_basic_tokens(""), 0)
        self.assertEqual(estimate_basic_tokens("   "), 0)

    def test_estimate_basic_tokens_non_empty(self):
        sample = "OpenAI ve Gemini aslında token yoklama yapar"
        tokens = estimate_basic_tokens(sample)
        self.assertGreater(tokens, 0)
        self.assertLess(tokens, len(sample.split()) * 3)

    def test_estimate_usage_counts(self):
        prompt = "Listele 1-2-3"
        response = "Tamam"
        usage = estimate_usage(prompt, response)
        self.assertEqual(usage["total_tokens"], usage["prompt_tokens"] + usage["response_tokens"])
        self.assertGreaterEqual(usage["prompt_tokens"], 1)
        self.assertGreaterEqual(usage["response_tokens"], 1)


class RealLLMClientTests(unittest.TestCase):
    def test_generate_yields_usage_and_cost(self):
        client = RealLLMClient(model="test-model")
        result = client.generate("Token testi")
        self.assertEqual(result.model, "test-model")
        self.assertTrue(result.response.startswith("[simulated test-model response]"))
        self.assertIn("usage", result.__dict__)
        self.assertGreater(result.usage["total_tokens"], 0)
        self.assertIsInstance(result.estimated_cost, float)

    def test_logs_cost_with_tracker(self):
        tracker = CostTracker()
        tracker.calculate_cost = MagicMock(return_value=0.12345678)
        tracker.log_cost = MagicMock()
        client = RealLLMClient(model="test-model", provider="codex", cost_tracker=tracker)
        result = client.generate("Token testi")
        self.assertEqual(result.estimated_cost, 0.12345678)
        tracker.log_cost.assert_called_once_with(
            "codex",
            "test-model",
            result.usage["prompt_tokens"],
            result.usage["response_tokens"],
            0.12345678,
        )


if __name__ == "__main__":
    unittest.main()
