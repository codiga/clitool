"""Save a ruleset into a file

Usage:
    codiga-export-ruleset [options]

Global options:
    -r RULESET               Name of the ruleset
    -s SERVER_URL            URL of the rosie server to use
Example:
    $ codiga-export-ruleset -r "python-security" -s "https://analysis.codiga.io/analyze"
"""

import os
import json
import logging
import sys
import time

import docopt
from codiga.model.rosie_rule import RosieRule, ELEMENT_CHECKED_TO_ENTITY_CHECKED_FOR_API

from codiga.rosie.api import ROSIE_URL, analyze_rosie
from .constants import DEFAULT_TIMEOUT, API_TOKEN_ENVIRONMENT_VARIABLE
from .graphql.common import do_graphql_query
from .graphql.rosie import graphql_get_rulesets, graphql_get_ruleset
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

    ruleset_name = options['-r']
    server_url_optional = options['-s']


    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.INFO)

    failed_rules = []
    try:
        if not ruleset_name:
            log.info('Please specify a ruleset name!')
            sys.exit(1)
        server_url = ROSIE_URL
        if server_url_optional is not None:
            server_url = server_url_optional

        ruleset = graphql_get_ruleset(None, ruleset_name)

        if ruleset is None:
            print("ruleset not found")
            sys.exit(1)

        for rule in ruleset['rules']:
            if rule['elementChecked'] in ELEMENT_CHECKED_TO_ENTITY_CHECKED_FOR_API:
                element_checked = ELEMENT_CHECKED_TO_ENTITY_CHECKED_FOR_API[rule['elementChecked']]
            else:
                element_checked = None
            rule_object = RosieRule(
                f"{ruleset_name}/{rule['name']}",
                rule['content'],
                rule['language'],
                rule['ruleType'],
                element_checked,
                rule['pattern']
            )
            rule_fail = False
            for test in rule['tests']:
                violations = analyze_rosie(test['name'], rule['language'], "utf-8", test['content'], [rule_object], server_url)
                if len(violations) > 0 and not test['shouldFail']:
                    print("should not fail and has violations")
                    print(test['name'])
                    rule_fail = True
                if len(violations) == 0 and test['shouldFail']:
                    print("should fail and has no violations")
                    print(test['name'])
                    rule_fail = True

            if rule_fail:
                failed_rules.append(rule['name'])

        if len(failed_rules) == 0:
            print("All rules passed")
        else:
            failed_rules_str = ",".join(failed_rules)
            print(f"Failed rules: {failed_rules_str}")

        sys.exit(0)
    except KeyboardInterrupt:  # pragma: no cover
        log.info('Aborted')
        sys.exit(1)
    sys.exit(0)
