"""Trigger new code analysis on code-inspector.io

Usage:
    code-inspector [options]

Global options:
    -v --verbose      Print the results of the requests when succeeding

Example:
    $ code-inspector
"""

import os
import logging
import sys

import docopt
import requests

from .version import __version__

API_ENDPOINT = 'https://www.code-inspector.com/api/project/analysis/new'

log = logging.getLogger('code-inspector')


def main(argv=None):
    options = docopt.docopt(__doc__, argv=argv, version=__version__)

    level = logging.DEBUG if options['--verbose'] else logging.INFO
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

        payload = {'accessKey': access_key, 'secretKey': secret_key}
        response = requests.post(API_ENDPOINT, json=payload)
        log.debug('text: {0}'.format(response.text))
        response_json = response.json()
        if response.status_code != 200:
            log.info('Non 200 error code')
            sys.exit(1)

        log.debug('Request sent, response: {0}'.format(response_json['status']))

    except KeyboardInterrupt:  # pragma: no cover
        log.info('Aborted')
        sys.exit(1)
    sys.exit(0)
