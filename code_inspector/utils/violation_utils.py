"""
Functions to help manage violations.
"""
from typing import List

from code_inspector.model.violation import Violation


def filter_violations(violations: List[Violation],
                      exclude_categories: list[str],
                      exclude_severities: list[int]) -> List[Violation]:
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