"""Get the status of a project on Code-Inspector

Usage:
    codiga-project [options]

Global options:
    -p PROJECT_NAME          Project name to show
Example:
    $ codiga-project -p "MY SUPER PROJECT"
"""

import os
import json
import logging
import sys

import docopt

from .constants import API_TOKEN_ENVIRONMENT_VARIABLE
from .graphql.common import do_graphql_query

from .version import __version__

log = logging.getLogger('codiga')


def get_project_information(api_token: str, project_name: str) -> dict:
    """
    Get the project information with the latest analysis data using the project name
    :param api_token: the api token to the GraphQL API
    :param project_name: name of the project
    :return: the project identifier or None is exception or non-existent project.
    """
    query = """
    {
        project (name: \"""" + project_name + """\") {
            id
            name
            lastAnalysis{
              status
              techdebt{
                score
                grade
              } 
              summary { 
                violations
                duplicates
                duplicated_lines
                complexFunctions
                longFunctions
                longFunctionsRate
                complexFunctionsRate
                violationsSeverity1
                violationsSeverity2
                violationsSeverity3
                violationsSeverity4
                violationsDesign
                violationsSafety
                violationsUnknown
                violationsSecurity
                violationsDeployment
                violationsCode_style
                violationsPerformance
                violationsError_prone
                violationsDocumentation
                violationsBest_practice
              }
            }
        }
    }
    """
    response_json = do_graphql_query(api_token, {"query": query})
    return response_json['project']


def main(argv=None):
    """
    Make the magic happen.
    :param argv:
    :return:
    """
    options = docopt.docopt(__doc__, argv=argv, version=__version__)

    project_name = options['-p']

    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.INFO)

    try:
        api_token = os.environ.get(API_TOKEN_ENVIRONMENT_VARIABLE)

        if not project_name:
            log.info('Project name not defined!')
            sys.exit(1)

        if not api_token:
            log.info('API Token not defined!')
            sys.exit(1)

        project_information = get_project_information(api_token, project_name)
        if not project_information:
            log.error("Cannot get project information")
            sys.exit(1)

        print(json.dumps(project_information, indent=4))

        sys.exit(0)
    except KeyboardInterrupt:  # pragma: no cover
        log.info('Aborted')
        sys.exit(1)
    sys.exit(0)
