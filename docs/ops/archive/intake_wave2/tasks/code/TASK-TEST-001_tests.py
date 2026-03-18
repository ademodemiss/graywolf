import unittest
from tasks.code.TASK-TEST-001_main import divide
class TestDivide(unittest.TestCase):
    def test_divide_positive(self):
        self.assertEqual(divide(4, 2), 2)
    def test_divide_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            divide(1, 0)
