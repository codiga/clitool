"""
Utilities to interact with git.
"""
import logging
import shutil
import subprocess
from typing import List

from code_inspector.exceptions.git_command_exception import GitCommandException

COMMAND_DIFF = 'diff'


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
        logging.error(process.stderr)
        GitCommandException("error when executing a git command")

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
    return execute_git_command([COMMAND_DIFF, revision1, revision2])
