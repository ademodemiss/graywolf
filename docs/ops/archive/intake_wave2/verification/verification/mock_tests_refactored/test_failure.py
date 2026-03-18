import unittest

class FailureTest(unittest.TestCase):
    def test_fail(self):
        self.assertEqual(1, 0) # This will fail
