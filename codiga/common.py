import logging

log = logging.getLogger('codiga')

GRADE_EXCELLENT = "EXCELLENT"
GRADE_GOOD = "GOOD"
GRADE_NEUTRAL = "NEUTRAL"
GRADE_WARNING = "WARNING"
GRADE_CRITICAL = "CRITICAL"
GRADE_UNKNOWN = "UNKNOWN"
GRADE_UNAVAILABLE = "UNAVAILABLE"


def is_grade_lower(grade, minimum_grade):
    """
    return is a given grade is lower than a given grade.
    :param grade: the current grade
    :param minimum_grade: minimum grade to expect.
    :return:
    """

    grade = grade.upper()
    minimum_grade = minimum_grade.upper()

    if grade == GRADE_EXCELLENT:
        return False

    if grade == GRADE_GOOD:
        if minimum_grade in [GRADE_EXCELLENT]:
            return True
        return False

    if grade == GRADE_NEUTRAL:
        if minimum_grade in [GRADE_EXCELLENT, GRADE_GOOD]:
            return True
        return False

    if grade == GRADE_WARNING:
        if minimum_grade in [GRADE_EXCELLENT, GRADE_GOOD, GRADE_NEUTRAL]:
            return True
        return False

    if grade == GRADE_CRITICAL:
        if minimum_grade in [GRADE_EXCELLENT, GRADE_GOOD, GRADE_NEUTRAL, GRADE_WARNING]:
            return True
        return False

    if grade == GRADE_UNKNOWN:
        if minimum_grade in [GRADE_UNKNOWN]:
            return False
        return True

    if grade == GRADE_UNAVAILABLE:
        return False

    return False
