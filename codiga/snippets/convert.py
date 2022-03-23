import base64
import re


def convert_camel_case_to_snake_case(string):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', string).lower()

def convert_variables_in_recipes(recipe_content):
    """
    Replace VS code-style user-variables with Codiga variables
    :param recipe_content: the recipe content as text
    :return: the recipe formatted for Codiga
    """
    pattern = re.compile('\\${(\d+):([^}]+)}')
    iterator = pattern.finditer(recipe_content)
    to_replace = {}
    for match in iterator:
        original_text = recipe_content[match.start():match.end()]
        replace_text = f"&[USER_INPUT:{match.group(1)}:{match.group(2)}]"
        to_replace[original_text] = replace_text


    pattern = re.compile('\\$(\d+)')
    iterator = pattern.finditer(recipe_content)
    for match in iterator:
        original_text = recipe_content[match.start():match.end()]
        replace_text = f"&[USER_INPUT:{match.group(1)}]"
        recipe_content = recipe_content.replace(original_text, replace_text)
        to_replace[original_text] = replace_text

    for key in to_replace:
        recipe_content = recipe_content.replace(key, to_replace[key])
    return recipe_content

def fix_shortcut(shortcut):
    replace_characters = shortcut.replace("!", "").replace("/", "").replace("<", "").replace(">", "").replace("(", "").replace(")", "")
    replace_underscores = shortcut.replace("-", "_")
    camel_case = convert_camel_case_to_snake_case(replace_underscores)
    return camel_case


def convert_snippet_file_content_to_codiga(json_content):
    """
    Convert a file file content to a snippet for Codiga
    :param json_content:
    :return:
    """
    recipes = []
    for snippet_name in json_content.keys():
        snippet = json_content[snippet_name]
        snippet_content = "\n".join(snippet["body"])
        snippet_prefix = fix_shortcut(snippet["prefix"])
        snippet_content = convert_variables_in_recipes(snippet_content)

        # Replace indent by the codiga indentation style
        snippet_content = snippet_content.replace("\t", "&[CODIGA_INDENT]")

        snippet_content_base64 = base64.b64encode(snippet_content.encode('utf-8')).decode('utf-8')

        if snippet_name is not None and snippet_content_base64 is not None and snippet_prefix is not None:
            recipe_payload = {
                "name": snippet_name,
                "content": snippet_content_base64,
                "shortcut": snippet_prefix
            }
            recipes.append(recipe_payload)
    return recipes


