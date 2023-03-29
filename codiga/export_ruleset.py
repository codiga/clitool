"""Save a ruleset into a file

Usage:
    codiga-export-ruleset [options]

Global options:
    -r RULESET               Name of the rulesets (e.g. python-security,python-best-practices)
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
from .rosie.ruleset import element_checked_api_to_json
from .version import __version__

logging.basicConfig()

log = logging.getLogger('codiga')



def main(argv=None):
    """
    Make the magic happen.
    :param argv:
    :return:
    """
    options = docopt.docopt(__doc__, argv=argv, version=__version__)

    ruleset_names = options['-r']
    filename = options['-f']


    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.INFO)

    try:
        api_token = os.environ.get(API_TOKEN_ENVIRONMENT_VARIABLE)

        if not api_token:
            log.info('%s environment variable not defined!', API_TOKEN_ENVIRONMENT_VARIABLE)
            sys.exit(1)


        if not ruleset_names:
            log.info('Please specify a ruleset name (or multiple separated by a comma)!')
            sys.exit(1)
        rules = []
        for ruleset_name in ruleset_names.split(","):
            ruleset = graphql_get_ruleset(api_token, ruleset_name)
            if ruleset is None:
                continue

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
