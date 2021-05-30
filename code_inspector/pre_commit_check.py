"""Check that when doing a push, the code being pushed does not contain any violation detected by
Code Inspector.

Usage:
    code-inspector-pre-commit-check [options]


Global options:
    --exclude-categories <list-of-strings>  Violations with categories you want to exclude
    --exclude-severities <list-of-integer>  Violations which severities you want to ignore separated by commas
    --remote-sha <string>                   The remote SHA. If new branch, the script passes automatically
    --local-sha <string>                    The local SHA being pushed
    --project-name <string>                 Name of the project on Code Inspector
    --max-timeout-sec <timeout>             Maximum time to wait before the analysis is done (in secs). Default to 60.
Example:
    $ code-inspector-pre-commit-check -p "MY SUPER PROJECT" --local-sha <sha1> --remote-sha <sha2> --exclude-categories=Documentation --exclude-severities 3,4

Note:
    Make sure your API keys are defined using CODE_INSPECTOR_ACCESS_KEY and CODE_INSPECTOR_SECRET_KEY
"""
from typing import List, Dict, Set

import docopt
import os
import logging
import sys

import unidiff
from unidiff import PatchSet

from .constants import BLANK_SHA
from .utils.file_utils import associate_files_with_language
from .utils.git import get_git_binary, get_diff
from .utils.patch_utils import get_added_or_modified_lines
from .version import __version__

logging.basicConfig()

log: logging.Logger = logging.getLogger('code-inspector')


def check_push(project_name: str, local_sha: str, remote_sha: str,
               exclude_categories: list[str], exclude_severities: list[int], max_timeout_secs: int):
    """
    Check that the
    :param project_name:
    :param local_sha:
    :param remote_sha:
    :param exclude_categories:
    :param exclude_severities:
    :param max_timeout_secs:
    :return:
    """
    # If the remote sha does not exist, we do not check this revision.
    if remote_sha == BLANK_SHA:
        return

    diff_content = get_diff(remote_sha, local_sha)
    print("DIFF")
    patch_set = PatchSet(diff_content)
    added_lines: Dict[str, Set[int]] = get_added_or_modified_lines(patch_set)
    files_to_analyze: Set[str] = set(added_lines.keys())

    files_with_languages: dict[str, str] = associate_files_with_language(files_to_analyze)

    

    print("files to analyze %s", files_to_analyze)


def main(argv=None):
    """
    Main entrypoint.
    :param argv:
    :return:
    """
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.INFO)
    options = docopt.docopt(__doc__, argv=argv, help=True, version=__version__)

    exclude_categories: str = options['--exclude-categories']
    exclude_severities: str = options['--exclude-severities']
    remote_sha: str = options['--remote-sha']
    local_sha: str = options['--local-sha']
    project_name: str = options['--project-name']
    max_timeout_sec: str = options['--max-timeout-sec']
    access_key: str = os.environ.get('CODE_INSPECTOR_ACCESS_KEY')
    secret_key: str = os.environ.get('CODE_INSPECTOR_SECRET_KEY')
    exclude_severities_list: list[str] = []
    exclude_categories_list: list[str] = []

    if not access_key:
        log.error('CODE_INSPECTOR_ACCESS_KEY environment variable not defined!')
        sys.exit(1)

    if not secret_key:
        log.error('CODE_INSPECTOR_SECRET_KEY not defined!')
        sys.exit(1)

    if not project_name:
        log.error('Project name not defined')
        sys.exit(1)

    if not remote_sha:
        log.error('remote_sha not defined')
        sys.exit(1)

    if not local_sha:
        log.error('local_sha not defined')
        sys.exit(1)

    if not get_git_binary():
        log.error("cannot locate git")
        sys.exit(1)

    if exclude_severities:
        exclude_severities_list = exclude_severities.split(",")

    if exclude_categories:
        exclude_categories_list = exclude_categories.split(",")

    if not max_timeout_sec:
        max_timeout_sec = 60

    check_push(
        project_name=project_name,
        exclude_categories=exclude_categories_list,
        exclude_severities=exclude_severities_list,
        local_sha=local_sha,
        remote_sha=remote_sha,
        max_timeout_secs=max_timeout_sec)
    sys.exit(0)
