"""Import Codiga Snippet from VS Code in Codiga.io

Usage:
    codiga-snippets-imports [options]

Options:
    --visibility <public|private>               Visibility of the snippet (public or private)
    --language=<language>                       Language of the snippet (Java, Javascript, Typescript, etc)
    --file=</path/to/snippets.json>             File to import (this or --url must be passed)
    --url=<https://path/to/snippets.json>       URL to the snippet to import (this or --file must be passed)
    --cookbook=<cookbook-id>                    add recipe to a cookbook (optional)
    --shortcut-prefix=<prefix>                  prefix for all snippets (optional)
    --staging                                   Use staging endpoint (debugging only)

Example:
    $ codiga-snippets-imports --visibility public --language Javascript --url https://url/to/snippets.json
"""

import os
import json
import logging
import sys
import requests

import docopt


from .constants import DEFAULT_TIMEOUT, API_TOKEN_ENVIRONMENT_VARIABLE
from .graphql.recipe import post_recipe
from .snippets.convert import convert_snippet_file_content_to_codiga
from .version import __version__

logging.basicConfig()

log = logging.getLogger('codiga')

VALID_LANGUAGES = ["Docker",
                   "Objectivec",
                   "Terraform",
                   "Json",
                   "Yaml",
                   "Swift",
                   "Solidity",
                   "Sql",
                   "Shell",
                   "Scala",
                   "Rust",
                   "Ruby",
                   "Php",
                   "Python",
                   "Perl",
                   "Kotlin",
                   "Html",
                   "Haskell",
                   "Go",
                   "Apex",
                   "Css",
                   "Dart",
                   "Javascript",
                   "Typescript",
                   "C",
                   "Cpp",
                   "Csharp",
                   "Python",
                   "Java"]

def main(argv=None):
    """
    Main function that makes the magic happen.
    :param argv:
    :return:
    """
    options = docopt.docopt(__doc__, argv=argv, version=__version__)

    visibility = options['--visibility']
    language = options['--language']
    file = options['--file']
    url = options['--url']
    use_staging = options['--staging']
    cookbook = options['--cookbook']
    shortcut_prefix = options['--shortcut-prefix']

    log.addHandler(logging.StreamHandler())

    log.setLevel(logging.INFO)

    if visibility not in ["public", "private"]:
        print("Invalid visibility, should be public or private")
        sys.exit(1)

    if language not in VALID_LANGUAGES:
        print(f"Invalid language, valid languages: {','.join(VALID_LANGUAGES)}")
        sys.exit(1)

    if not url and not file:
        print("no --url and no --file passed, please provide at least one method")
        sys.exit(1)

    if url and file:
        print("both --url and --file passed, please provide at least one method")
        sys.exit(1)

    if cookbook:
        try:
            cookbook_id = int(cookbook)
        except ValueError:
            print("Invalid cookbook id")
            sys.exit(-1)
    else:
        cookbook_id = None

    try:
        api_token = os.environ.get(API_TOKEN_ENVIRONMENT_VARIABLE)

        # API Token must be defined. If not, we rely on the old access key/secret key.
        if not api_token:
            log.info('%s environment variable not defined!', API_TOKEN_ENVIRONMENT_VARIABLE)
            sys.exit(1)

        if url:
            request = requests.get(url, timeout=10)
            content = request.json()
        if file:
            if os.path.isfile(file):
                with open(file) as myfile:
                    file_content = myfile.read()
                    try:
                        content = json.loads(file_content)
                    except json.decoder.JSONDecodeError:
                        # Cannot read the file
                        print("cannot read file, invalid JSON")
                        sys.exit(1)
            else:
                print("file not found")
                sys.exit(1)

        if not content:
            print("no content read")
            sys.exit(1)

        codiga_recipes = convert_snippet_file_content_to_codiga(content, shortcut_prefix)
        recipe_index = 0
        for codiga_recipe in codiga_recipes:
            result = post_recipe(api_token, codiga_recipe, language, visibility == "public", cookbook_id, use_staging)
            if result and "data" in result and result["data"]['createAssistantRecipe'] and result["data"]['createAssistantRecipe']['id']:
                if use_staging:
                    url = f"https://app-staging.codiga.io/assistant/recipe/{result['data']['createAssistantRecipe']['id']}/view"
                else:
                    url =f"https://app.codiga.io/assistant/recipe/{result['data']['createAssistantRecipe']['id']}/view"
                print(f"[SUCCESS] {recipe_index} Recipe {codiga_recipe['name']} at: {url}")
            else:
                if "errors" in result:
                    print(f"[ERROR] {recipe_index} Error when posting recipe {codiga_recipe['name']}: {result['errors'][0]['message']}")
                else:
                    print(f"[ERROR] {recipe_index} Error when posting recipe {codiga_recipe['name']}")
                    print(result)
            recipe_index = recipe_index + 1
        sys.exit(0)
    except KeyboardInterrupt:  # pragma: no cover
        log.info('Aborted')
        sys.exit(1)
