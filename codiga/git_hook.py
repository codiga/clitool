"""Check that when doing a push, the code being pushed does not contain any violation detected by
Codiga. Your project MUST have a codiga.yml file at the root. See https://app.codiga.io/hub/rulesets
for rulesets.

For an example how to use it in a Git hook, check https://doc.codiga.io/docs/git-hooks/

Usage:
    codiga-git-hook [options]

Global options:
    --remote-sha <string>                   The remote SHA. If new branch, the script passes automatically
    --local-sha <string>                    The local SHA being pushed
    --max-timeout-sec <timeout>             Maximum time to wait before the analysis is done (in secs). Default to 60.

Example:
    $ codiga-git-hook --local-sha <sha1> --remote-sha <sha2>

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
from .graphql.rosie import get_rulesets
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


def analyze_file(rosie_rules: typing.List[RosieRule], filename: str, language: str) -> List[Violation]:
    """
    Analyze a file using a GraphQL query
    :param rosie_rules: rules to use
    :param language: language of the file
    :param filename: the name of the filename
    :return: the list of violations found
    """

    violations: List[Violation] = []

    # Read the file being pushed/sent
    try:
        with open(filename, "r") as file:
            code: str = file.read()
            code_base64 = base64.b64encode(code.encode('utf-8')).decode('utf-8')
            res = analyze_rosie(filename, language, "utf-8", code_base64, rosie_rules)
            violations.extend(res)
    except FileNotFoundError:
        logging.error("Cannot open file %s", filename)
        return violations
    return violations


def analyze_files(files_with_language: Dict[str, str],
                  rosie_rules: typing.List[RosieRule],
                  max_timeout_secs: int) -> Dict[str, List[Violation]]:
    """
    Analyze all files and return the list of violations for all of them. In order
    to speed up analysis, use a thread pool to launch multiple analysis.

    :param files_with_language: Dictionary with the files and their languages
    :param rosie_rules: list of rules to use
    :param max_timeout_secs: how long before the analysis fails (in seconds)
    :return: dictionary with the file name as key and list of violations as a result
    """
    threads: Dict[str, Thread] = {}
    result: Dict[str, List[Violation]] = {}
    executor = ThreadPoolExecutor(4)
    files_to_analyze = files_with_language.keys()
    deadline = time.time() + max_timeout_secs

    # Submit all threads to be executed.
    for filename in files_to_analyze:
        thread = executor.submit(analyze_file, rosie_rules, filename, files_with_language[filename])
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


def check_push(local_sha: str, remote_sha: str, max_timeout_secs: int):
    """
    Check the current push.
    :param local_sha:
    :param remote_sha:
    :param max_timeout_secs:
    :return:
    """
    api_token: str = os.environ.get(API_TOKEN_ENVIRONMENT_VARIABLE)
    # If the remote sha does not exist, we do not check this revision.
    if remote_sha == BLANK_SHA:
        print("Push seems to originate from a new branch, trying to find ancestor commit.")
        remote_sha = find_closest_sha()
        if not remote_sha:
            print("Tried to find closest SHA but did not found any. Returning 0", file=sys.stderr)
            sys.exit(0)

    if remote_sha == local_sha:
        print(f"Remote and local sha are the same ({remote_sha}), skipping verification", file=sys.stderr)
        sys.exit(0)

    all_violations: List[Violation] = []
    diff_content = get_diff(remote_sha, local_sha)

    if not diff_content:
        log.error("cannot read diff")
        sys.exit(2)

    root_directory = get_root_directory()

    if not root_directory:
        log.error("Cannot find the repository root directory")
        sys.exit(1)

    ruleset_files = f"{root_directory.strip()}/codiga.yml"
    if not os.path.isfile(ruleset_files):
        log.error("no codiga.yml file found at the root of the directory (searching for %s)", ruleset_files)
        sys.exit(2)

    rulesets = get_rulesets_from_codigafile(ruleset_files)

    log.info("using the following rulesets %s", rulesets)

    rules = get_rulesets(api_token, rulesets)
    rosie_rules: typing.List[RosieRule] = convert_rules_to_rosie_rules(rules)

    log.info("found %s rules", len(rosie_rules))

    patch_set = PatchSet(diff_content)
    added_lines: Dict[str, Set[int]] = get_added_or_modified_lines(patch_set)
    files_to_analyze: Set[str] = set(added_lines.keys())

    # Associate a file with a language.
    # If a file does not match a language, just do not include it (can be binary blob,
    # anything not analyzable by Codiga.
    files_with_languages: Dict[str, str] = associate_files_with_language(files_to_analyze)

    # Show the list of files to analyze
    if len(files_with_languages) > 0:
        print("Analyzing {0} files: {1}".format(len(files_with_languages), ",".join(files_with_languages)))
    else:
        print("No file to analyze")

    # First, analyze each file and get the list of violations.
    files_with_violations: Dict[str, List[Violation]] = analyze_files(files_with_languages, rosie_rules, max_timeout_secs)

    # Finally, filter the violations with the information with the diff. Only show the violations that have been
    # added in the diff being pushed.
    violations_per_file: Dict[str, List[Violation]] = {filename: filter_violations_for_diff(violations, added_lines.get(filename, [])) for filename, violations in files_with_violations.items()}

    # Put all violations in an array so that we can know how many violations we have.
    for violations in violations_per_file.values():
        all_violations.extend(violations)

    # If we have violations, print them to show the users where you have violations
    if len(all_violations) > 0:
        print("*** {0} violations found ***".format(len(all_violations)), file=sys.stderr)
        print_violations(violations_per_file)
        logging.info("Detected %s violations", len(all_violations))
        sys.exit(1)
    else:
        print("no violation found")


def main(argv=None):
    """
    Main entrypoint.
    :param argv:
    :return:
    """
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.INFO)
    options = docopt.docopt(__doc__, argv=argv, help=True, version=__version__)

    remote_sha: str = options['--remote-sha']
    local_sha: str = options['--local-sha']
    max_timeout_sec: str = options['--max-timeout-sec']
    api_token: str = os.environ.get(API_TOKEN_ENVIRONMENT_VARIABLE)

    if not api_token:
        log.error('%s environment variable not defined!', API_TOKEN_ENVIRONMENT_VARIABLE)
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

    try:
        check_push(
            local_sha=local_sha,
            remote_sha=remote_sha,
            max_timeout_secs=max_timeout_sec_int)
        sys.exit(0)
    except Exception:
        log.exception("unexpected error. Please send the trace to support@codiga.io")
