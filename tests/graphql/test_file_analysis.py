"""
Test for methods in graphql/file_analysis.py
"""

import unittest
from unittest.mock import patch

from codiga.graphql.file_analysis import graphql_get_file_analysis, graphql_create_file_analysis


class TestFileAnalysis(unittest.TestCase):
    """
    Tests for graphql/file_analysis.py
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
            graphql_get_file_analysis(None, 1)
        with self.assertRaises(ValueError):
            graphql_get_file_analysis("blo", None)

    @patch('codiga.graphql.file_analysis.do_graphql_query')
    def test_graphql_get_file_analysis_check_call(self, do_graphql_query_mock):
        """
        Check that we call the right method when arguments are valid
        :return:
        """
        graphql_get_file_analysis("api_token", 1)
        do_graphql_query_mock.assert_called()

    @patch('codiga.graphql.file_analysis.do_graphql_query')
    def test_graphql_create_file_analysis_check_call(self, do_graphql_query_mock):
        """
        Check that we call the right method when arguments are valid
        :return:
        """
        graphql_create_file_analysis("api_token", "filename", "language", "content", 1)
        query = {'query': '\n    mutation{\n        createFileAnalysis (\n            language: language,\n            code: "content",\n            filename: "filename"\n            projectId: 1\n        )\n    }\n    '}
        do_graphql_query_mock.assert_called_with("api_token", query)

        graphql_create_file_analysis("api_token", "filename", "language", "content", None)
        query = {'query': '\n    mutation{\n        createFileAnalysis (\n            language: language,\n            code: "content",\n            filename: "filename"\n            projectId: null\n        )\n    }\n    '}
        do_graphql_query_mock.assert_called_with("api_token", query)
