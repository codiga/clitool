"""
Functions to help manage violations.
"""
from typing import List

from codiga.model.violation import Violation


def filter_violations_for_diff(violations: List[Violation], lines_to_keep: List[int]) -> List[Violation]:
    """
    Filter violations and keep only the one at specific lines.
    :param violations: the list of violations
    :param lines_to_keep: the list of lines to keep
    :return: the list of violations that match the lines in the [[lines_to_keep]] array
    """
    result: List[Violation] = []
    for violation in violations:
        if violation.line in lines_to_keep:
            result.append(violation)
    return result
