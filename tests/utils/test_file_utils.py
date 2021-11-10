"""
Test for methods in utils/test_file_utils.py
"""

import unittest
from typing import Set

from codiga.utils.file_utils import LANGUAGE_C, LANGUAGE_JAVA, LANGUAGE_DOCKER, get_language_for_file, \
    associate_files_with_language


class TestFileUtils(unittest.TestCase):
    """
    Test methods for the utils/file_utils.py
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_language_for_file(self):
        """
        Test that we correctly identify the language based on the file extension or prefix
        :return:
        """
        self.assertEqual(LANGUAGE_C, get_language_for_file("foobar.c"))
        self.assertEqual(LANGUAGE_JAVA, get_language_for_file("foobar.java"))
        self.assertEqual(LANGUAGE_DOCKER, get_language_for_file("Dockerfile"))
        self.assertIsNone(get_language_for_file("noextension"))

    def test_associate_files_with_language(self):
        """
        Test that we correctly associate a filename with the language and also filter
        files with no language
        :return:
        """
        filenames: Set[str] = set()
        filenames.add("noextension")
        filenames.add("foobar.c")
        filenames.add("foobar.java")
        association = associate_files_with_language(filenames)
        self.assertEqual(LANGUAGE_C, association.get("foobar.c"))
        self.assertEqual(LANGUAGE_JAVA, association.get("foobar.java"))
        self.assertFalse("noextension" in association)
