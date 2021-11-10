"""
Utility methods to manipulate patch. These utility methods
rely mostly on the unidiff module.
"""

from typing import Set, Dict

from unidiff import PatchSet


def get_added_or_modified_lines(patch_set: PatchSet) -> Dict[str, Set[int]]:
    """
    Parse a patchset and returns all the modified lines in return.
    :param patch_set: the patch set being processed
    :return: a dictionary with the key are the files added or modified and the list of all added lines
    """
    added_lines: Dict[str, Set[int]] = {}
    for patch in patch_set:
        if patch.is_added_file or patch.is_modified_file:
            added_lines[patch.path] = set()
            for hunk in patch:
                for target_line in hunk.target_lines():
                    if target_line.is_added:
                        added_lines[patch.path].add(target_line.target_line_no)
    return added_lines
