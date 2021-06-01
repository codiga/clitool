"""Get the status of a project on Code-Inspector

Usage:
    code-inspector-analyze [options]

Global options:
    -p PROJECT_NAME          Project name to show
    -w                       Wait for the analysis to complete and print results
    -t TIMEOUT               Timeout to wait for the job completion (default 600 seconds)
Example:
    $ code-inspector-analyze -p "MY SUPER PROJECT"
"""

import os
import json
import logging
import sys
import time

import docopt

from .constants import DEFAULT_TIMEOUT
from .graphql.common import do_graphql_query
from .version import __version__

logging.basicConfig()

log = logging.getLogger('code-inspector')


def analyze(access_key, secret_key, project_name):
    """
    Get the project information with the latest analysis data using the project name
    :param access_key: the access key to the GraphQL API
    :param secret_key: the secret key to the GraphQL API
    :param project_name: name of the project
    :return: the project identifier or None is exception or non-existent project.
    """
    args = []
    args.append("name: \"" + project_name + "\"")
    args_string = ",".join(args)
    query = """
        mutation { scheduleAnalysis(""" + args_string + """){id}}
    """
    response_json = do_graphql_query(access_key, secret_key, {"query": query})

    if not response_json:
        return None

    return response_json['scheduleAnalysis']


def get_analysis(access_key, secret_key, analysis_id):
    """
    Get an analysis using its ID
    :param access_key: access key to poll the API
    :param secret_key: secret key to poll the API
    :param analysis_id: the identifier of the analysis we want to poll
    :return: the return code depending on the results or some processing error
    """

    query = """
        {
          analysis(id: """ + str(analysis_id) + """){
            id
            status
            techdebt{
              grade
              score
            }
            summary{
              duplicates
              violations
            }
          }
        }
        """
    response_json = do_graphql_query(access_key, secret_key, {"query": query})
    return response_json['analysis']


def main(argv=None):
    """
    Make the magic happen.
    :param argv:
    :return:
    """
    options = docopt.docopt(__doc__, argv=argv, version=__version__)

    project_name = options['-p']
    wait = True if options['-w'] else False

    try:
        timeout = int(options['-t']) if options['-t'] else DEFAULT_TIMEOUT
    except ValueError:
        timeout = DEFAULT_TIMEOUT

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

        analysis = analyze(access_key, secret_key, project_name)

        if not analysis:
            log.error("Cannot start new analysis")
            sys.exit(1)

        if wait:
            analysis_id = analysis['id']
            deadline = time.time() + timeout

            while True:
                now = time.time()
                if now > deadline:
                    log.error("Deadline expired")
                    sys.exit(1)

                poll_analysis = get_analysis(access_key, secret_key, analysis_id)
                if poll_analysis['status'].upper() not in ["DONE", "ERROR", "SAME_REVISION"]:
                    log.debug("analysis not completed yet")
                    time.sleep(5)
                    continue

                print(json.dumps(poll_analysis, indent=4))
                sys.exit(0)
        else:
            log.info("Analysis started")
            log.info(json.dumps(analysis))

        sys.exit(0)
    except KeyboardInterrupt:  # pragma: no cover
        log.info('Aborted')
        sys.exit(1)
    sys.exit(0)
