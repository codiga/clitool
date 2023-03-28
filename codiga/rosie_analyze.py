"""Analyze a file from Rosie and get the result

Usage:
    codiga-rosie-analyze --ruleset=<ruleset1>... --file=</path/to/file>

Global options:
    --ruleset <string>                   Ruleset to use to analyze
    --file <string>                      The file being analyzed

Example:
    $ codiga-rosie-analyze --ruleset ruleset1 --ruleset ruleset2 --file <file>

Note:
    Make sure your API keys are defined using CODIGA_API_TOKEN
"""
import typing
from concurrent.futures import ThreadPoolExecutor
import os
import logging
import sys
import base64
from threading import Thread
import time
from time import sleep
from typing import List, Dict, Set

from unidiff import PatchSet
import docopt

from .constants import BLANK_SHA, API_TOKEN_ENVIRONMENT_VARIABLE
from .graphql.rosie import graphql_get_rulesets
from .model.rosie_rule import RosieRule, convert_rules_to_rosie_rules
from .model.violation import Violation
from .rosie.api import analyze_rosie
from .rosie.ruleset import get_rulesets_from_codigafile
from .utils.file_utils import associate_files_with_language
from .utils.git import get_git_binary, get_diff, find_closest_sha, get_root_directory
from .utils.patch_utils import get_added_or_modified_lines
from .utils.violation_utils import filter_violations_for_diff
from .version import __version__

logging.basicConfig()

log: logging.Logger = logging.getLogger('codiga')



def main(argv=None):
    """
    Main entrypoint.
    :param argv:
    :return:
    """
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.INFO)
    options = docopt.docopt(__doc__, argv=argv, help=True, version=__version__)

    rulesets: List[str] = options['--ruleset']
    file: typing.Optional[str] = options['--file']
    api_token: str = os.environ.get(API_TOKEN_ENVIRONMENT_VARIABLE)

    if not api_token:
        log.error('%s environment variable not defined!', API_TOKEN_ENVIRONMENT_VARIABLE)
        sys.exit(1)

    if not file:
        log.error('file is missing')
        sys.exit(1)

    if not rulesets:
        log.error('rulesets are missing')
        sys.exit(1)

    try:
        print(f"rules {rulesets}")
        print(f"file {file}")
        sys.exit(0)
    except Exception:
        log.exception("unexpected error. Please send the trace to support@codiga.io")
