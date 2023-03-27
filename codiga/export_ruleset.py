"""Save a ruleset into a file

Usage:
    codiga-export-ruleset [options]

Global options:
    -r RULESET               Name of the ruleset
    -f FILE                  File to store the ruleset
Example:
    $ codiga-export-ruleset -r "python-security" -f rules.json
"""

import os
import json
import logging
import sys
import time

import docopt

from .constants import DEFAULT_TIMEOUT, API_TOKEN_ENVIRONMENT_VARIABLE
from .graphql.common import do_graphql_query
from .graphql.rosie import graphql_get_rulesets, graphql_get_ruleset
from .version import __version__

logging.basicConfig()

log = logging.getLogger('codiga')


def element_checked_api_to_json(value):
    if value is None:
        return None
    if value.lower() == "any":
        return "ANY"
    elif value.lower() == "assignment":
        return "ASSIGNMENT"
    elif value.lower() == "classdefinition":
        return "CLASS_DEFINITION"
    elif value.lower() == "forloop":
        return "FOR_LOOP"
    elif value.lower() == "functioncall":
        return "FUNCTION_CALL"
    elif value.lower() == "functiondefinition":
        return "FUNCTION_DEFINITION"
    elif value.lower() == "functionexpression":
        return "FUNCTION_EXPRESSION"
    elif value.lower() == "htmlelement":
        return "HTML_ELEMENT"
    elif value.lower() == "ifstatement":
        return "IF_STATEMENT"
    elif value.lower() == "interface":
        return "INTERFACE"
    elif value.lower() == "importstatement":
        return "IMPORT_STATEMENT"
    elif value.lower() == "variabledeclaration":
        return "VARIABLE_DECLARATION"
    elif value.lower() == "tryblock":
        return "TRY_BLOCK"
    elif value.lower() == "type":
        return "TYPE"
    return None

def main(argv=None):
    """
    Make the magic happen.
    :param argv:
    :return:
    """
    options = docopt.docopt(__doc__, argv=argv, version=__version__)

    ruleset_name = options['-r']
    filename = options['-f']


    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.INFO)

    try:
        api_token = os.environ.get(API_TOKEN_ENVIRONMENT_VARIABLE)

        if not api_token:
            log.info('%s environment variable not defined!', API_TOKEN_ENVIRONMENT_VARIABLE)
            sys.exit(1)


        if not ruleset_name:
            log.info('Please specify a ruleset name!')
            sys.exit(1)

        ruleset = graphql_get_ruleset(api_token, ruleset_name)
        rules = []
        for r in ruleset['rules']:
            new_object = {
                "name": f"{ruleset_name}/{r['name']}",
                "code": r['content'],
                "language": r['language'].upper(),
                "pattern": r['pattern'],
                "ruleType": "AST_CHECK" if r['ruleType'].lower() == "ast" else "PATTERN",
                "entityChecked": element_checked_api_to_json(r['elementChecked'])
            }
            rules.append(new_object)

        with open(filename, "w") as outfile:
            content = {
                "rules": rules
            }
            outfile.write(json.dumps(content))


        sys.exit(0)
    except KeyboardInterrupt:  # pragma: no cover
        log.info('Aborted')
        sys.exit(1)
    sys.exit(0)
