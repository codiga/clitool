"""
Functions to help manage violations.
"""
from typing import List

from code_inspector.model.violation import Violation


def filter_violations(violations: List[Violation],
                      exclude_categories: List[str],
                      exclude_severities: List[int]) -> List[Violation]:
    """
    Filter violations according to rules specified by the user.
    :param violations: all violations
    :param exclude_categories: categories to exclude
    :param exclude_severities: severities to exclude
    :return: list of filtered violations
    """
    exclude_categories_uppercase = map(lambda x: x.upper(), exclude_categories)
    result: List[Violation] = []
    for violation in violations:
        if violation.category.upper() in exclude_categories_uppercase:
            continue
        if violation.severity in exclude_severities:
            continue
        result.append(violation)
    return result


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
