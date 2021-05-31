"""Get the status of a project on Code-Inspector

Usage:
    code-inspector-project [options]

Global options:
    -p PROJECT_NAME          Project name to show
Example:
    $ code-inspector-project -p "MY SUPER PROJECT"
"""

import os
import json
import logging
import sys

import docopt
from .graphql.common import do_graphql_query

from .version import __version__

log = logging.getLogger('code-inspector')


def get_project_information(access_key: str, secret_key: str, project_name: str) -> dict:
    """
    Get the project information with the latest analysis data using the project name
    :param access_key: the access key to the GraphQL API
    :param secret_key: the secret key to the GraphQL API
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
    response_json = do_graphql_query(access_key, secret_key, {"query": query})
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
        access_key = os.environ.get('CODE_INSPECTOR_ACCESS_KEY')
        secret_key = os.environ.get('CODE_INSPECTOR_SECRET_KEY')

        if not access_key:
            log.info('CODE_INSPECTOR_ACCESS_KEY environment variable not defined!')
            sys.exit(1)

        if not secret_key:
            log.info('CODE_INSPECTOR_SECRET_KEY not defined!')
            sys.exit(1)

        if not project_name:
            log.info('Project name not defined!')
            sys.exit(1)

        project_information = get_project_information(access_key, secret_key, project_name)
        if not project_information:
            log.error("Cannot get project information")
            sys.exit(1)

        print(json.dumps(project_information, indent=4))

        sys.exit(0)
    except KeyboardInterrupt:  # pragma: no cover
        log.info('Aborted')
        sys.exit(1)
    sys.exit(0)
