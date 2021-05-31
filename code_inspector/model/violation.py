"""
Defines a violation for a single file
"""


class Violation:
    """
    Represent violation for a single file.
    """
    def __init__(self, **kwargs):
        self.id = id
        self.line = kwargs['line']
        self.description = kwargs['description']
        self.severity = kwargs['severity']
        self.category = kwargs['category']
        self.line_count = kwargs['line_count']
        self.tool = kwargs['tool']
        self.language = kwargs['language']
        self.rule = kwargs['rule']
        self.rule_url = kwargs['rule_url']