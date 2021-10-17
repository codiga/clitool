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
from concurrent.futures import ThreadPoolExecutor
import os
import logging
import sys
from threading import Thread
import time
from time import sleep
from typing import List, Dict, Set

from unidiff import PatchSet
import docopt

from .constants import BLANK_SHA
from .graphql.constants import STATUS_DONE, STATUS_ERROR
from .graphql.file_analysis import graphql_create_file_analysis, graphql_get_file_analysis
from .graphql.project import graphql_get_project_info
from .model.violation import Violation
from .utils.file_utils import associate_files_with_language
from .utils.git import get_git_binary, get_diff, find_closest_sha
from .utils.patch_utils import get_added_or_modified_lines
from .utils.violation_utils import filter_violations, filter_violations_for_diff
from .version import __version__

logging.basicConfig()

log: logging.Logger = logging.getLogger('code-inspector')


def analyze_file(filename: str, language: str, project_id: int) -> List[Violation]:
    """
    Analyze a file using a GraphQL query
    :param project_id: the identifier of the project to analyze
    :param language: language of the file
    :param filename: the name of the filename
    :return: the list of violations found
    """
    access_key: str = os.environ.get('CODE_INSPECTOR_ACCESS_KEY')
    secret_key: str = os.environ.get('CODE_INSPECTOR_SECRET_KEY')

    violations: List[Violation] = []
    file_analysis_id: int = None

    # Read the file being pushed/sent
    try:
        with open(filename, "r") as file:
            code = file.read()

            file_analysis_id = graphql_create_file_analysis(
                access_key=access_key,
                secret_key=secret_key,
                filename=filename,
                language=language,
                project_id=project_id,
                content=code
            )
    except FileNotFoundError:
        logging.error("Cannot open file %s", filename)
        return violations

    # Make the analysis on Code Inspector and wait for the analysis to complete.
    while True:
        file_analysis = graphql_get_file_analysis(
            access_key=access_key,
            secret_key=secret_key,
            file_analysis_id=file_analysis_id
        )
        if file_analysis['getFileAnalysis']['status'] == STATUS_ERROR:
            break

        if file_analysis['getFileAnalysis']['status'] == STATUS_DONE:
            for graphql_violation in file_analysis['getFileAnalysis']['violations']:
                violations.append(Violation(**graphql_violation))
            break

        time.sleep(0.5)
        continue
    return violations


def analyze_files(project_name: str,
                  files_with_language: Dict[str, str],
                  max_timeout_secs: int) -> Dict[str, List[Violation]]:
    """
    Analyze all files and return the list of violations for all of them. In order
    to speed up analysis, use a thread pool to launch multiple analysis.

    :param project_name: name of the project to analyze on Code Inspecto
    :param files_with_language: Dictionary with the files and their languages
    :param max_timeout_secs: how long before the analysis fails (in seconds)
    :return: dictionary with the file name as key and list of violations as a result
    """
    threads: Dict[str, Thread] = {}
    result: Dict[str, List[Violation]] = {}
    executor = ThreadPoolExecutor(4)
    project_id = None
    files_to_analyze = files_with_language.keys()
    deadline = time.time() + max_timeout_secs
    access_key: str = os.environ.get('CODE_INSPECTOR_ACCESS_KEY')
    secret_key: str = os.environ.get('CODE_INSPECTOR_SECRET_KEY')

    # Get the project identifier based on the project name
    if project_name:
        project_info = graphql_get_project_info(
            access_key=access_key,
            secret_key=secret_key,
            project_name=project_name
        )

        if not project_info:
            print("Project {0} not found".format(project_name), file=sys.stderr)
            sys.exit(2)

        if project_info:
            project_id = int(project_info['id'])

    # Submit all threads to be executed.
    for filename in files_to_analyze:
        thread = executor.submit(analyze_file, filename, files_with_language[filename], project_id)
        threads[filename] = thread

    # Wait for threads completion
    for filename in threads:
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
            print("{0}:{1} {2}".format(filename, violation.line, violation.description), file=sys.stderr)


def check_push(project_name: str, local_sha: str, remote_sha: str,
               exclude_categories: List[str], exclude_severities: List[int], max_timeout_secs: int):
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
        print("Push seems to originate from a new branch, trying to find ancestor commit.")
        remote_sha = find_closest_sha()
        if not remote_sha:
            print("Tried to find closest SHA but did not found any. Returning 0", file=sys.stderr)
            sys.exit(0)

    if remote_sha == local_sha:
        print("Remote and local sha are the same ({0}), skipping verification"
              .format(remote_sha), file=sys.stderr)
        sys.exit(0)

    all_violations: List[Violation] = []
    diff_content = get_diff(remote_sha, local_sha)
    patch_set = PatchSet(diff_content)
    added_lines: Dict[str, Set[int]] = get_added_or_modified_lines(patch_set)
    files_to_analyze: Set[str] = set(added_lines.keys())

    # Associate a file with a language.
    # If a file does not match a language, just do not include it (can be binary blob,
    # anything not analyzable by Code Inspector.
    files_with_languages: Dict[str, str] = associate_files_with_language(files_to_analyze)

    # Show the list of files to analyze
    if len(files_with_languages) > 0:
        print("Analyzing {0} files: {1}".format(len(files_with_languages), ",".join(files_with_languages)))
    else:
        print("No file to analyze")

    # First, analyze each file and get the list of violations.
    files_with_violations: Dict[str, List[Violation]] = analyze_files(project_name, files_with_languages, max_timeout_secs)

    # Then, filter the violations based on the list of excluded categories and severities passed as arguments.
    files_with_violations_filtered: Dict[str, List[Violation]] = {filename: filter_violations(violations, exclude_categories, exclude_severities) for filename, violations in files_with_violations.items()}

    # Finally, filter the violations with the information with the diff. Only show the violations that have been
    # added in the diff being pushed.
    violations_per_file: Dict[str, List[Violation]] = {filename: filter_violations_for_diff(violations, added_lines.get(filename, [])) for filename, violations in files_with_violations_filtered.items()}

    # Put all violations in an array so that we can know how many violations we have.
    for violations in violations_per_file.values():
        all_violations.extend(violations)

    # If we have violations, print them to show the users where you have violations
    if len(all_violations) > 0:
        print("*** {0} violations found ***".format(len(all_violations)), file=sys.stderr)
        print_violations(violations_per_file)
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
    exclude_severities_list: List[str] = []
    exclude_categories_list: List[str] = []
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

    exclude_severities_list_int: List[int] = []
    max_timeout_sec_int: int

    # Get the timeout to a seconds value
    if not max_timeout_sec:
        max_timeout_sec_int = 60
    else:
        try:
            max_timeout_sec_int = int(max_timeout_sec)
        except ValueError:
            print("timeout value should be an integer", file=sys.stderr)
            sys.exit(2)

    # Convert the severity list into list of int
    for severity in exclude_severities_list:
        try:
            exclude_severities_list_int.append(int(severity))
        except ValueError:
            print("excluded severities should be an int", file=sys.stderr)
            sys.exit(2)

    check_push(
        project_name=project_name,
        exclude_categories=exclude_categories_list,
        exclude_severities=exclude_severities_list_int,
        local_sha=local_sha,
        remote_sha=remote_sha,
        max_timeout_secs=max_timeout_sec_int)
    sys.exit(0)
