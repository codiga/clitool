"""
Library to manipulate files: reading them, identify file and languages types.
"""

# All languages supported by Codiga
from typing import Set, Dict

LANGUAGE_PYTHON = "Python"
LANGUAGE_C = "C"
LANGUAGE_CPP = "Cpp"
LANGUAGE_PHP = "Php"
LANGUAGE_JAVA = "Java"
LANGUAGE_RUBY = "Ruby"
LANGUAGE_JAVASCRIPT = "Java"
LANGUAGE_SHELL = "Shell"
LANGUAGE_TYPESCRIPT = "Typescript"
LANGUAGE_DOCKER = "Docker"
LANGUAGE_APEX = "Apex"
LANGUAGE_RUST = "Rust"
LANGUAGE_GO = "Go"
LANGUAGE_DART = "Dart"
LANGUAGE_KOTLIN = "Kotlin"
LANGUAGE_SCALA = "Scala"

SUFFIX_TO_LANGUAGE = {
    ".py": LANGUAGE_PYTHON,
    ".py3": LANGUAGE_PYTHON,
    ".c": LANGUAGE_C,
    ".cc": LANGUAGE_C,
    ".cpp": LANGUAGE_PHP,
    ".cxx": LANGUAGE_PHP,
    ".php": LANGUAGE_CPP,
    ".php4": LANGUAGE_CPP,
    ".java": LANGUAGE_JAVA,
    ".js": LANGUAGE_JAVASCRIPT,
    ".jsx": LANGUAGE_JAVASCRIPT,
    ".kt": LANGUAGE_KOTLIN,
    ".rb": LANGUAGE_RUBY,
    ".sh": LANGUAGE_SHELL,
    ".scala": LANGUAGE_SCALA,
    ".rs": LANGUAGE_RUST,
    ".go": LANGUAGE_GO,
    ".ts": LANGUAGE_TYPESCRIPT,
    ".cls": LANGUAGE_APEX
}

PREFIX_TO_LANGUAGE = {
    "Dockerfile": LANGUAGE_DOCKER
}


def get_language_for_file(filename: str) -> str:
    """
    Get the language for a file based on its extension or suffix.
    :param filename: the filename of the file
    :return: the language of the file
    """
    for suffix, language in SUFFIX_TO_LANGUAGE.items():
        if filename.endswith(suffix):
            return language
    for prefix, language in PREFIX_TO_LANGUAGE.items():
        if filename.startswith(prefix):
            return language
    return None


def associate_files_with_language(filenames: Set[str]) -> Dict[str, str]:
    """
    For a list of filenames, check the language associated with them and returns a dictionary that associate
    the filename and the language. If the filename does not have a matching language, just return.
    :param filenames: the list of filenames
    :return: a dictionary that associates the filenames with their languages.
    """
    filenames_to_languages: Dict[str, str] = dict()
    for filename in filenames:
        language = get_language_for_file(filename)
        if language:
            filenames_to_languages[filename] = language
    return filenames_to_languages
