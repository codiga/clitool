import unittest
from unittest.mock import patch

from code_inspector.common import is_grade_lower
from code_inspector.graphql.constants import STATUS_DONE
from code_inspector.pre_commit_check import analyze_file


class TestPreCommitCheck(unittest.TestCase):
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


    @patch('code_inspector.pre_commit_check.graphql_create_file_analysis')
    @patch('code_inspector.pre_commit_check.graphql_get_file_analysis')
    def test_analyze_file_success(self, graphql_get_file_analysis, graphql_create_file_analysis):
        """
        Test that test the success case of analyze_file
        :return:
        """
        ret1 = {
            'getFileAnalysis': {
                'status': STATUS_DONE,
                'violations': []
            }
        }
        ret2 = {
            'getFileAnalysis': {
                'status': STATUS_DONE,
                'violations': [
                    {
                        'line': 1,
                        'lineCount': 2,
                        'description': 'mydescription',
                        'rule': 'myrule',
                        'ruleUrl': 'rule_url',
                        'tool': 'mytool',
                        'category': 'Design',
                        'severity': 1,
                        'language': 'C'
                    }
                ]
            }
        }
        graphql_create_file_analysis.return_value = 1
        graphql_get_file_analysis.return_value = ret1
        res = analyze_file("LICENSE", "C", 1)
        self.assertTrue(len(res) == 0)

        graphql_get_file_analysis.return_value = ret2
        res = analyze_file("LICENSE", "C", 1)
        self.assertTrue(len(res) == 1)