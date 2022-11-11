import unittest
from unittest.mock import patch

from codiga.graphql.constants import STATUS_DONE
from codiga.git_hook import analyze_file


class TestPreCommitCheck(unittest.TestCase):
    """
    Test git_hook.py
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_analyze_file_file_does_not_exists(self):
        """
        Test to analyze a file that does not exists
        :return:
        """
        res = analyze_file("myfilethatdoesnotexists", "C", 1)
        self.assertTrue(len(res) == 0)

