import unittest

from self_improve.error_analyzer import ErrorAnalyzer


class ErrorAnalyzerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = ErrorAnalyzer()

    def test_classify_permission_error(self):
        result = self.analyzer.classify_failure("permission denied: /etc/passwd")
        self.assertEqual(result["category"], "permission_error")
        self.assertIn("elevate_permissions", result["replan_hint"])

    def test_classify_unknown_error_defaults(self):
        result = self.analyzer.classify_failure("something weird happened")
        self.assertEqual(result["category"], "unknown_error")
        self.assertEqual(result["replan_hint"], self.analyzer.replan_hint_for_category("unknown_error"))

    def test_hint_lookup(self):
        hint = self.analyzer.replan_hint_for_category("rate_limit_error")
        self.assertEqual(hint, "slow_down")
        self.assertEqual(self.analyzer.replan_hint_for_category("nonexistent"), "retry_general")


if __name__ == "__main__":
    unittest.main()
