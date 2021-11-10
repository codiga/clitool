"""Compare two projects using Codiga engine.

Usage:
    codiga-compare [options]

Global options:
    -v --verbose             Print the results of the requests when succeeding
    -w --wait                Wait for the analysis to complete and print results
    -t TIMEOUT               Timeout to wait for the job completion (default 600 seconds)
    -p PROJECT_NAME          Project name to build
    --url URL                URL of the target repository
    --kind KIND              Kind of target repository (Git, Github, Gitlab, Bitbucket) - required
    --username USERNAME      Username to checkout the project (optional)
    --password PASSWORD      Password to checkout the target repository (optional)
    --target-branch <STR>    Target branch to analyze (optional)
    --target-revision <STR>  Target revision to analyze (optional)
Example:
    $ codiga-compare
"""

import os
import json
import logging
import sys
import time

import docopt


import codiga.constants as constants
from .graphql.common import do_graphql_query
from .version import __version__

logging.basicConfig()

log = logging.getLogger('codiga')


def get_project_id(api_token, project_name):
    """
    Get the project identifier from the GraphQL API
    :param api_token: the access token to the GraphQL API
    :param project_name: name of the project
    :return: the project identifier or None is exception or non-existent project.
    """
    try:
        query = """
        {
            project (name: \"""" + project_name + """\") {
                id
                name
            }
        }
        """
        response_json = do_graphql_query(api_token, {"query": query})
        return response_json["project"]["id"]
    except KeyError:
        log.error("Error while getting project identifier")
        return None


def start_compare_analysis(api_token, project_id, kind, url, username, password, target_branch, target_revision):
    """
    Get the project identifier from the GraphQL API
    :param api_token: the access token to the GraphQL API
    :param project_id: identifier of the project to use as source
    :param kind: kind of the target repositiory (Github, Gitlab, Git)
    :param url: URL of the target repository
    :param username: username of the target repository
    :param password: password of the target repository
    :return: the project identifier or None is exception or non-existent project.
    """
    try:
        args = []
        args.append("projectId: " + str(project_id))
        args.append("targetKind: " + kind)
        args.append("targetUrl: \"" + url + "\"")

        if target_revision:
            args.append("targetRevision: \"" + target_revision + "\"")

        if target_branch:
            args.append("targetBranch: \"" + target_branch + "\"")

        args_string = ",".join(args)

        query = """
            mutation { createCompareAnalysis(""" + args_string + """){id}}
        """

        response_json = do_graphql_query(api_token, {"query": query})
        return response_json["createCompareAnalysis"]["id"]
    except KeyError:
        log.error("Error while starting new analysis")
        return None


def poll_compare_analysis(api_token, compare_analysis_id, timeout):
    """
    Poll the compare analysis, get the results and return a value depending on the results.
    :param api_token: access token to poll the API
    :param compare_analysis_id: the identifier of the analysis to poll
    :param timeout: how long do we wait/poll before returning any issue?
    :return: the return code depending on the results or some processing error
    """
    deadline_sec = time.time() + int(timeout)
    while True:
        time.sleep(5)

        if deadline_sec < time.time():
            log.error("Timeout expired")
            sys.exit(1)

        compare_analysis = get_compare_analysis(api_token, compare_analysis_id)

        if not compare_analysis:
            log.info("Did not find compare analysis object")
            continue

        if not compare_analysis['status'].upper() in ["DONE", "ERROR"]:
            log.debug("compare analysis in status %s", compare_analysis['status'])
            continue

        if not compare_analysis['sourceAnalysis']:
            log.info("no source analysis")
            continue

        if not compare_analysis['targetAnalysis']:
            log.info("no target analysis")
            continue

        # Get source and target analysis objects
        source_analysis = compare_analysis['sourceAnalysis']
        target_analysis = compare_analysis['targetAnalysis']

        source_status = source_analysis['status']
        target_status = target_analysis['status']

        if source_status.upper() not in ["DONE", "ERROR", "SAME_REVISION"] or target_status.upper() not in ["DONE", "ERROR", "SAME_REVISION"]:
            log.error("source analysis or target analysis are not done successfully. source status = %s, "
                      "target status = %s", source_analysis['status'], target_analysis['status'])
            continue

        if source_status.upper() == "ERROR":
            log.error("source status is error")
            return 3
        elif target_status.upper() == "ERROR":
            log.error("target status is error")
            return 4
        else:
            print(json.dumps(compare_analysis, indent=4))
            diff_violations = target_analysis['summary']['violations'] - source_analysis['summary']['violations']
            diff_duplicates = target_analysis['summary']['violations'] - source_analysis['summary']['violations']

            if diff_violations > 0:
                return 5
            if diff_duplicates > 0:
                return 6
            return 0


def get_compare_analysis(api_token, compare_analysis_id):
    """
    Poll the compare analysis, get the results and return a value depending on the results.
    :param api_token: access token to poll the API
    :param compare_analysis_id: the identifier of the analysis to poll
    :param wait_and_print_results: True if we should wait and print the results
    :param timeout: how long do we wait/poll before returning any issue?
    :return: the return code depending on the results or some processing error
    """

    query = """
        {
          analysisCompare(id: """ + str(compare_analysis_id) + """){
            id
            status
            sourceAnalysis{
              status
              summary{
                duplicates
                violations
              }
            }
            targetAnalysis{
              status
              summary{
                duplicates
                violations
              }
            }
          }
        }
        """
    response_json = do_graphql_query(api_token, {"query": query})
    return response_json['analysisCompare']


def main(argv=None):
    """
    Make the magic happen.
    :param argv:
    :return:
    """
    options = docopt.docopt(__doc__, argv=argv, version=__version__)

    level = logging.DEBUG if options['--verbose'] else logging.INFO
    timeout = options['-t'] if options['-t'] else constants.DEFAULT_TIMEOUT
    project_name = options['-p']
    url = options['--url']
    kind = options['--kind']
    username = options['--username']
    password = options['--password']
    target_branch = options['--target-branch']
    target_revision = options['--target-revision']

    log.addHandler(logging.StreamHandler())
    log.setLevel(level)

    try:
        api_token = os.environ.get(constants.API_TOKEN_ENVIRONMENT_VARIABLE)

        if not api_token:
            log.info('%s environment variable not defined!', constants.API_TOKEN_ENVIRONMENT_VARIABLE)
            sys.exit(1)

        if not project_name:
            log.info('Project name not defined!')
            sys.exit(1)

        if not kind:
            log.info('Kind not defined!')
            sys.exit(1)

        if not url:
            log.info('URL not defined!')
            sys.exit(1)

        if kind not in constants.VALID_SCM_KINDS:
            log.info("Invalid kind")
            sys.exit(1)

        project_id = get_project_id(api_token, project_name)

        if not project_id:
            log.error("Cannot get information about your project, exiting")
            sys.exit(2)

        compare_analysis_id = start_compare_analysis(api_token, project_id,
                                                     kind, url, username, password, target_branch, target_revision)
        if not compare_analysis_id:
            log.error("Cannot start a new comparison, exiting")
            sys.exit(3)

        ret = poll_compare_analysis(api_token, compare_analysis_id, timeout)
        log.debug("done, returning %s", ret)
        sys.exit(ret)
    except KeyboardInterrupt:  # pragma: no cover
        log.info('Aborted')
        sys.exit(1)
    sys.exit(0)
