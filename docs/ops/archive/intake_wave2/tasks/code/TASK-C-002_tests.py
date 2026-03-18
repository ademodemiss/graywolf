import unittest
from tasks.code.TASK-C-002_main import subtract
class TestSubtract(unittest.TestCase):
    def test_subtract_positive(self):
        self.assertEqual(subtract(5, 2), 3)
