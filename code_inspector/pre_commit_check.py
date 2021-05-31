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
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from time import sleep
from typing import List, Dict, Set

import docopt
import os
import logging
import sys

from unidiff import PatchSet

from .constants import BLANK_SHA
from .graphql.file_analysis import graphql_create_file_analysis
from .model.violation import Violation
from .utils.file_utils import associate_files_with_language
from .utils.git import get_git_binary, get_diff
from .utils.patch_utils import get_added_or_modified_lines
from .utils.violation_utils import filter_violations
from .version import __version__

logging.basicConfig()

log: logging.Logger = logging.getLogger('code-inspector')


def graphql_get_file_analysis(file_analysis_id):
    pass


def analyze_file(filename: str, language: str, project_id: int) -> List[Violation]:
    """
    Analyze a file using a GraphQL query
    :param project_id: the identifier of the project to analyze
    :param filename: the name of the filename
    :return: the list of violations found
    """
    print("Thread started")
    file_analysis_id: int = None
    with open(filename, "r") as f:
        code = f.read()

        file_analysis_id = graphql_create_file_analysis(
            filename=filename,
            language=language,
            project_id=project_id,
            content=code
        )

    while True:
        file_analysis_status = graphql_get_file_analysis(file_analysis_id)

    return []


def analyze_files(project_name: str, files_with_language: Dict[str, str], max_timeout_secs: int) -> Dict[str, List[Violation]]:
    """
    Analyze all files and return the list of violations for all of them. In order
    to speed up analysis, use a thread pool to launch multiple analysis.

    :param project_name: name of the project to analyze on Code Inspecto
    :param files_with_language: Dictionary with the files and their languages
    :return: dictionary with the file name as key and list of violations as a result
    """
    threads: Dict[str, Thread] = {}
    result: Dict[str, List[Violation]] = {}
    executor = ThreadPoolExecutor(4)
    project_id = None
    files_to_analyze = files_with_language.keys()
    deadline = time.time() + max_timeout_secs

    # Submit all threads to be executed.
    for filename in files_to_analyze:
        thread = executor.submit(analyze_file, filename, files_with_language[filename], project_id)
        threads[filename] = thread

    # Wait for threads completion
    for filename in threads.keys():
        while not threads[filename].done():
            sleep(0.5)

        # If we reach the deadline, just cancel the threads and raise a timeout error.
        if time.time() > deadline:
            for thread in threads.values():
                thread.cancel()
                raise TimeoutError("max execution time reached")

        result[filename] = threads[filename].result()

    return result


def print_violations(files_with_violations: Dict[str, List[Violation]]):
    """
    Print all the violations from all the files.

    :param files_with_violations: a dictionary that contains all violations for each file.
    :return:
    """
    for filename in files_with_violations.keys():
        for violation in files_with_violations[filename]:
            logging.error("%s:%s %s", filename, violation.line, violation.description)


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

    all_violations: List[Violation] = []
    diff_content = get_diff(remote_sha, local_sha)
    patch_set = PatchSet(diff_content)
    added_lines: Dict[str, Set[int]] = get_added_or_modified_lines(patch_set)
    files_to_analyze: Set[str] = set(added_lines.keys())

    files_with_languages: dict[str, str] = associate_files_with_language(files_to_analyze)

    files_with_violations: Dict[str, List[Violation]] = analyze_files(project_name, files_with_languages, max_timeout_secs)
    files_with_violations_filtered: Dict[str, List[Violation]] = {filename: filter_violations(violations, exclude_categories, exclude_severities) for filename, violations in files_with_violations.items()}

    for violations in files_with_violations_filtered.values():
        all_violations.extend(violations)

    if len(all_violations) > 0:
        logging.error("*** Violations found ***")
        print_violations(files_with_violations_filtered)
        logging.info("Detected %s violations", len(all_violations))
        sys.exit(1)


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
