"""Trigger new code analysis on code-inspector.io

Usage:
    code-inspector [options]

Global options:
    -v --verbose      Print the results of the requests when succeeding
    -w --wait         Wait for the analysis to complete and print results
    -t TIMEOUT        Timeout to wait for the job completion (default 600 seconds)
Example:
    $ code-inspector
"""

import os
import logging
import sys

import docopt
import requests
import time

from .version import __version__

API_ENDPOINT_ANALYSIS_NEW = 'https://www.code-inspector.com/api/project/analysis/new'
API_ENDPOINT_ANALYSIS_STATUS = 'https://www.code-inspector.com/api/project/analysis/status'
API_ENDPOINT_PROJECT_STATUS = 'https://www.code-inspector.com/api/project/analysis/status'

DEFAULT_TIMEOUT = 600  # 10 minutes

log = logging.getLogger('code-inspector')


def main(argv=None):
    options = docopt.docopt(__doc__, argv=argv, version=__version__)

    level = logging.DEBUG if options['--verbose'] else logging.INFO
    wait_and_print_results = True if options['--wait'] else False
    timeout = options['-t'] if options['-t'] else DEFAULT_TIMEOUT

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

        payload = {'access_key': access_key, 'secret_key': secret_key}
        response = requests.post(API_ENDPOINT_ANALYSIS_NEW, json=payload)
        response_json = response.json()
        if response.status_code != 200:
            log.info('Failed to send a new job')
            sys.exit(1)

        # If we do not wait for completion, we exit directly and give the server answer.
        if not wait_and_print_results:
            log.info('status: {0}'.format(response_json['status']))
            sys.exit(0)

        analysis_id = response_json['analysis_id']
        project_name = response_json['project_name']

        # If there is no analysis id provided in the answer, exit
        if not analysis_id:
            log.error("Unable to start a new analysis")
            sys.exit(1)

        log.debug("New analysis started for project {0}, id: {1}".format(project_name, analysis_id))

        # What is the deadline to complete everything.
        deadline_sec = time.time() + int(timeout)
        while True:
            # If we reach the timeout, just exit
            if deadline_sec < time.time():
                log.error("Timeout, analysis was not completed on time")
                sys.exit(1)

            # Payload to get the status of the new triggered analysis
            payload = {'access_key': access_key, 'secret_key': secret_key, 'analysis_id': analysis_id}
            response = requests.post(API_ENDPOINT_ANALYSIS_STATUS, json=payload)

            # Response from the API
            log.debug('text: {0}'.format(response.text))
            response_json = response.json()

            # If we get a 200, this is a bad request, we exit.
            if response.status_code != 200:
                log.info('Failed to read job status')
                sys.exit(1)

            # The status of the analysis, it can be scheduled, inprogress, done, error or same_revision.
            # It is done only when done, error or same_revision.
            status = response_json['analysis_status']

            # Analysis is done, exiting!
            if status.lower() in ['same_revision', 'error', 'done']:
                print(response.text)
                sys.exit(0)
            time.sleep(10)

    except KeyboardInterrupt:  # pragma: no cover
        log.info('Aborted')
        sys.exit(1)
    sys.exit(0)