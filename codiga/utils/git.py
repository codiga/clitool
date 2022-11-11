"""
Utilities to interact with git.
"""
import logging
import shutil
import subprocess
import sys
from typing import List, Optional

from codiga.exceptions.git_command_exception import GitCommandException

COMMAND_DIFF = 'diff'


def get_current_branch() -> Optional[str]:
    """
    Returns the name of the current branch we are on
    Use the following command git rev-parse --abbrev-ref HEAD
    :return:
    """
    try:
        return execute_git_command(["rev-parse", "--abbrev-ref", "HEAD"]).strip('\n').strip()
    except GitCommandException:
        logging.error("Cannot find the current branch")
        return None


def get_main_branch() -> Optional[str]:
    """
    Returns the main branch used on a repository
    :return:
    """
    try:
        output = execute_git_command(["remote", "show", "origin"])
        for line in output.splitlines():
            line = line.strip('\n')
            if "HEAD branch:" in line:
                branch = line[line.index(":")+2:].strip('\n').strip()
                return branch
        return None
    except GitCommandException:
        logging.error("Cannot find the current branch")
        return None


def find_closest_sha() -> Optional[str]:
    """
    This function is called when we have a zero SHA, which means we are at the start of a branch.
    In that case, we try to find the closest commit with the HEAD branch from origin.
    :return: the closest sha between the current branch and the head branch.
    """
    current_branch = get_current_branch()
    main_branch = get_main_branch()

    if not current_branch or not main_branch:
        print("Cannot find the closest SHA (issue when finding branches)", file=sys.stderr)
        return None

    try:
        output = execute_git_command(["merge-base", "-a", main_branch, current_branch])
        output = output.strip('\n').strip()
        print('Closest SHA found between {0} and {1}: {2}'.format(current_branch, main_branch, output))
        return output
    except GitCommandException:
        logging.error("Cannot find the closest SHA")
        return None


def get_git_binary() -> str:
    """
    Return the path of the git binary
    :return:
    """
    return shutil.which("git")


def execute_git_command(arguments: List[str]) -> str:
    """
    Execute a git command with the arguments passed
    :param arguments: the arguments to pass to execute the git command
    :return: what is returned by the command
    """
    args: List[str] = [get_git_binary()]
    args.extend(arguments)

    try:
        process = subprocess.run(args, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        raise GitCommandException("error when executing a git command")

    if process.returncode == 0:
        return process.stdout.decode()
    logging.error(process.stderr)
    raise GitCommandException("error when executing a git command")


def get_diff(revision1: str, revision2: str):
    """
    Get the diff between two revisions
    :param revision1: the initial revision
    :param revision2: the target revision
    :return:
    """
    try:
        return execute_git_command([COMMAND_DIFF, revision1, revision2])
    except GitCommandException:
        return None


def get_root_directory():
    """
    Get the git root directory
    :return:
    """
    try:
        return execute_git_command(["rev-parse", "--show-toplevel"])
    except GitCommandException:
        return None