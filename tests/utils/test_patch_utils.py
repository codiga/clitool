"""
Test for methods in utils/test_patch_utils.py
"""

import unittest

from unidiff import PatchSet

from codiga.utils.patch_utils import get_added_or_modified_lines


class TestPatchUtils(unittest.TestCase):
    """
    Tests for utils/patch_utils.py
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_added_or_modified_lines(self):
        """
        Check that we correctly parse the patch and get the modified lines
        :return:
        """
        with open('tests/data/patch-example.patch') as file:
            diff_content = file.read()
        patch_set = PatchSet(diff_content)
        added_or_modified_lines = get_added_or_modified_lines(patch_set)

        # Make sure that only added lines are being detected.
        for i in range(9, 19):
            self.assertTrue(i in added_or_modified_lines.get('kernel/arch/x86/Makefile'))
        for i in range(1, 9):
            self.assertFalse(i in added_or_modified_lines.get('kernel/arch/x86/Makefile'))
        for i in range(19, 100):
            self.assertFalse(i in added_or_modified_lines.get('kernel/arch/x86/Makefile'))
        for i in range(1, 24):
            self.assertTrue(i in added_or_modified_lines.get('kernel/arch/x86/divisionbyzeroerror.c'))
        for i in range(25, 100):
            self.assertFalse(i in added_or_modified_lines.get('kernel/arch/x86/divisionbyzeroerror.c'))
