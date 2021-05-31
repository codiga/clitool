"""
Test for methods in graphql/file_analysis.py
"""

import unittest
from unittest.mock import patch

from code_inspector.graphql.file_analysis import graphql_get_file_analysis, graphql_create_file_analysis


class TestFileAnalysis(unittest.TestCase):
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
            graphql_get_file_analysis(None, "bla", 1)
        with self.assertRaises(ValueError):
            graphql_get_file_analysis("blo", None, 1)
        with self.assertRaises(ValueError):
            graphql_get_file_analysis("blo", "bli", None)

    @patch('code_inspector.graphql.file_analysis.do_graphql_query')
    def test_graphql_get_file_analysis_check_call(self, do_graphql_query_mock):
        """
        Check that we call the right method when arguments are valid
        :return:
        """
        graphql_get_file_analysis("accesskey", "secret_key", 1)
        do_graphql_query_mock.assert_called()

    @patch('code_inspector.graphql.file_analysis.do_graphql_query')
    def test_graphql_create_file_analysis_check_call(self, do_graphql_query_mock):
        """
        Check that we call the right method when arguments are valid
        :return:
        """
        graphql_create_file_analysis("accesskey", "secret_key", "filename", "language", "content", 1)
        query = {'query': '\n    mutation{\n        createFileAnalysis (\n            language: language,\n            code: "content",\n            filename: "filename"\n            projectId: 1\n        )\n    }\n    '}
        do_graphql_query_mock.assert_called_with("accesskey", "secret_key", query)

        graphql_create_file_analysis("accesskey", "secret_key", "filename", "language", "content", None)
        query = {'query': '\n    mutation{\n        createFileAnalysis (\n            language: language,\n            code: "content",\n            filename: "filename"\n            projectId: null\n        )\n    }\n    '}
        do_graphql_query_mock.assert_called_with("accesskey", "secret_key", query)