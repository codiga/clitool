"""
Test for methods in graphql/file_analysis.py
"""

import unittest
from unittest.mock import patch

from code_inspector.graphql.file_analysis import graphql_get_file_analysis, graphql_create_file_analysis
from code_inspector.graphql.project import graphql_get_project_info


class TestProject(unittest.TestCase):
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
            graphql_get_project_info(None, "bla", "project_name")
        with self.assertRaises(ValueError):
            graphql_get_project_info("blo", None, "project_name")
        with self.assertRaises(ValueError):
            graphql_get_project_info("blo", "bli", None)

    @patch('code_inspector.graphql.project.do_graphql_query')
    def test_graphql_create_file_analysis_check_call(self, do_graphql_query_mock):
        """
        Check that we return None when the project is not defined and the structure if project is defined.
        :return:
        """
        do_graphql_query_mock.return_value = {'project': 'bla'}
        data = graphql_get_project_info("accesskey", "secret_key", "project_name")
        do_graphql_query_mock.assert_called_with("accesskey", "secret_key", {'query': '\n        {\n          project(name:"project_name") {\n            id\n            name\n            public\n            description\n            status\n            owner{\n              username\n            }\n            level\n            analysesCount\n          }\n        }\n    '})
        self.assertEqual('bla', data)

        do_graphql_query_mock.return_value = {}
        data = graphql_get_project_info("accesskey", "secret_key", "project_name")
        do_graphql_query_mock.assert_called_with("accesskey", "secret_key", {'query': '\n        {\n          project(name:"project_name") {\n            id\n            name\n            public\n            description\n            status\n            owner{\n              username\n            }\n            level\n            analysesCount\n          }\n        }\n    '})
        self.assertIsNone(data)

