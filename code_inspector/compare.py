"""CLI tool for Continuous Integration with code-inspector.com

Usage:
    code-inspector [options]

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
    $ code-inspector
"""

import os
import json
import logging
import sys

import docopt
import requests
import time

from .version import __version__

GRAPHQL_ENDPOINT_URL = 'https://api.code-inspector.com/graphql'

DEFAULT_TIMEOUT = 1200  # 20 minutes
VALID_SCM_KINDS = ["Bitbucket", "Git", "Github", "Gitlab"]

log = logging.getLogger('code-inspector')


def do_graphql_query(access_key, secret_key, payload):
    """
    Do a GraphQL query
    :param access_key: the access key
    :param secret_key: the secret key
    :param payload: the payload we want to send.
    :return: the returned JSON object
    """
    headers = {"X-Access-Key": access_key,
               "X-Secret-Key": secret_key}
    response = requests.post(GRAPHQL_ENDPOINT_URL, json=payload, headers=headers)
    if response.status_code != 200:
        log.info('Failed to send payload')
        return None
    response_json = response.json()
    return response_json["data"]


def get_project_id(access_key, secret_key, project_name):
    """
    Get the project identifier from the GraphQL API
    :param access_key: the access key to the GraphQL API
    :param secret_key: the secret key to the GraphQL API
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
        response_json = do_graphql_query(access_key, secret_key, {"query": query})
        return response_json["project"]["id"]
    except Exception:
        log.error("Error while getting project identifier")
        return None


def start_compare_analysis(access_key, secret_key, project_id, kind, url, username, password, target_branch, target_revision):
    """
    Get the project identifier from the GraphQL API
    :param access_key: the access key to the GraphQL API
    :param secret_key: the secret key to the GraphQL API
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

        response_json = do_graphql_query(access_key, secret_key, {"query": query})
        return response_json["createCompareAnalysis"]["id"]
    except Exception:
        log.error("Error while starting new analysis")
        return None



def poll_compare_analysis(access_key, secret_key, compare_analysis_id, timeout):
    """
    Poll the compare analysis, get the results and return a value depending on the results.
    :param access_key: access key to poll the API
    :param secret_key: secret key to poll the API
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

        compare_analysis = get_compare_analysis(access_key, secret_key, compare_analysis_id)

        if not compare_analysis:
            log.info("Did not find compare analysis object")
            continue

        if not compare_analysis['status'].upper() in ["DONE", "ERROR"]:
            log.debug("compare analysis in status {0}".format(compare_analysis['status']))
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

        if source_status.upper() not in ["DONE", "ERROR"] or target_status.upper() not in ["DONE", "ERROR"]:
            log.error("source analysis or target analysis are not done successfully. source status = {0}, target status = {1}".format(source_analysis['status'], target_analysis['status']))
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


def get_compare_analysis(access_key, secret_key, compare_analysis_id):
    """
    Poll the compare analysis, get the results and return a value depending on the results.
    :param access_key: access key to poll the API
    :param secret_key: secret key to poll the API
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
    response_json = do_graphql_query(access_key, secret_key, {"query": query})
    return response_json['analysisCompare']


def main(argv=None):
    options = docopt.docopt(__doc__, argv=argv, version=__version__)

    level = logging.DEBUG if options['--verbose'] else logging.INFO
    timeout = options['-t'] if options['-t'] else DEFAULT_TIMEOUT
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

        if not kind:
            log.info('Kind not defined!')
            sys.exit(1)

        if not url:
            log.info('URL not defined!')
            sys.exit(1)

        if kind not in VALID_SCM_KINDS:
            log.info("Invalid kind")
            sys.exit(1)

        project_id = get_project_id(access_key, secret_key, project_name)

        if not project_id:
            log.error("Cannot get information about your project, exiting")
            sys.exit(2)

        compare_analysis_id = start_compare_analysis(access_key, secret_key, project_id, kind, url, username, password, target_branch, target_revision)
        if not compare_analysis_id:
            log.error("Cannot start a new comparison, exiting")
            sys.exit(3)

        ret = poll_compare_analysis(access_key, secret_key, compare_analysis_id, timeout)
        log.debug("done, returning {0}".format(ret))
        sys.exit(ret)
    except KeyboardInterrupt:  # pragma: no cover
        log.info('Aborted')
        sys.exit(1)
    sys.exit(0)