import unittest
from tasks.code.TASK-REV-001_main import multiply
class TestMultiply(unittest.TestCase):
    def test_multiply_positive(self):
        self.assertEqual(multiply(1, 2), 2)
