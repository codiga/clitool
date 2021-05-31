"""
Defines a violation for a single file
"""


class Violation:
    """
    Represent violation for a single file.
    """
    def __init__(self, **kwargs):
        self.identifier = kwargs['id']
        self.line = kwargs['line']
        self.description = kwargs['description']
        self.severity = kwargs['severity']
        self.category = kwargs['category']

        self.tool = kwargs['tool']
        self.language = kwargs['language']
        self.rule = kwargs['rule']

        if 'ruleUrl' in kwargs:
            self.rule_url = kwargs['ruleUrl']
        else:
            self.rule_url = None

        if 'lineCount' in kwargs:
            self.line_count = kwargs['lineCount']
        else:
            self.line_count = None
