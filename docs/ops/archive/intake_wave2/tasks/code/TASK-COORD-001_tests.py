import unittest
from tasks.code.TASK-COORD-001_main import add

class TestAdd(unittest.TestCase):
    def test_add_positive(self):
        self.assertEqual(add(1, 2), 3)
    def test_add_negative(self):
        self.assertEqual(add(-1, -1), -2)
    def test_add_zero(self):
        self.assertEqual(add(0, 0), 0)
