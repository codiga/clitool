"""
Test for methods in graphql/file_analysis.py
"""

import unittest
from unittest.mock import patch

from codiga.graphql.file_analysis import graphql_get_file_analysis, graphql_create_file_analysis
from codiga.graphql.project import graphql_get_project_info


class TestProject(unittest.TestCase):
    """
    Tests for graphql/project.py
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_graphql_get_file_analysis_invalid_argument(self):
        """
        Check that invalid arguments raise an exception
        :return:
        """
        with self.assertRaises(ValueError):
            graphql_get_project_info(None, "project_name")
        with self.assertRaises(ValueError):
            graphql_get_project_info("api_token", None)

    @patch('codiga.graphql.project.do_graphql_query')
    def test_graphql_create_file_analysis_check_call(self, do_graphql_query_mock):
        """
        Check that we return None when the project is not defined and the structure if project is defined.
        :return:
        """
        do_graphql_query_mock.return_value = {'project': 'bla'}
        data = graphql_get_project_info("api_token", "project_name")
        do_graphql_query_mock.assert_called_with("api_token", {'query': '\n        {\n          project(name:"project_name") {\n            id\n            name\n            public\n            description\n            status\n            owner{\n              username\n            }\n            level\n            analysesCount\n          }\n        }\n    '})
        self.assertEqual('bla', data)

        do_graphql_query_mock.return_value = {}
        data = graphql_get_project_info("api_token", "project_name")
        do_graphql_query_mock.assert_called_with("api_token", {'query': '\n        {\n          project(name:"project_name") {\n            id\n            name\n            public\n            description\n            status\n            owner{\n              username\n            }\n            level\n            analysesCount\n          }\n        }\n    '})
        self.assertIsNone(data)
