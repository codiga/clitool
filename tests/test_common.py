import unittest

from codiga.common import is_grade_lower


class TestCommon(unittest.TestCase):
    """
    Test code from common.py
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_violation_category(self):
        """
        Test the comparison for the quality score grade.
        :return:
        """
        self.assertFalse(is_grade_lower("EXCELLENT", "GOOD"))
