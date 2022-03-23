from codiga.graphql.common import do_graphql_query_with_api_token, do_graphql_query_with_api_token_complete


def post_recipe(api_token, recipe, language, is_public, cookbook_id, use_staging):
    """
    Post recipe on the API endpoint
    :param api_token: the API token to post the recipe
    :param recipe: the recipe to post
    :param cookbook_id: the cookbook id or None
    :param use_staging: if we use the staging endpoint or not
    :return:
    """
    is_public_str = "true" if is_public else "false"
    cookbook_str = str(cookbook_id) if cookbook_id is not None else "null"
    query = """
    mutation{
        createAssistantRecipe (
            code: \"""" + recipe["content"] + """\",
            name: \"""" + recipe["name"] + """\",
            language: """ + language + """,
            cookbookId: """ + cookbook_str + """,
            shortcut: \"""" + recipe["shortcut"] + """\",
            keywords: [],
            generateDescription: true,
            isPublic: """ + is_public_str + """
        ) {
            id
        }
    }
    """
    return do_graphql_query_with_api_token_complete(api_token, {"query": query}, use_staging)
