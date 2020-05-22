import unittest

from code_inspector.common import is_grade_lower


class TestModel(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_violation_category(self):
        self.assertFalse(is_grade_lower("EXCELLENT", "GOOD"))