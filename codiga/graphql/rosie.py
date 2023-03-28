import typing

"""
All the GraphQL queries for Rosie
"""

from codiga.graphql.common import do_graphql_query


def get_rulesets_name_string(ruleset_names: typing.List[str]):
    """
    Converts a List[str] into a string for graphql requests
    :param ruleset_names: List[str]
    :return: str
    """
    return "[\"" + ("\", \"".join(ruleset_names)) + "\"]"


def graphql_get_rulesets(api_token: str, ruleset_names: typing.List[str]):
    """
    Get rulesets by their names

    :param api_token: the API token to access the GraphQL API
    :param ruleset_names: the names of all rulesets to fetch
    """
    if not ruleset_names or not api_token:
        raise ValueError

    ruleset_names_string = get_rulesets_name_string(ruleset_names)
    query = """
        {
            ruleSetsForClient(names: """ + ruleset_names_string + """){
            id
            name
            rules(howmany: 10000, skip: 0){
              id
              name
              content
              language
              ruleType
              pattern
              patternMultiline
              elementChecked
              tests {
                id
                name
                shouldFail
                content
                description
              }
            }
          }
        }"""
    data = do_graphql_query(api_token, {"query": query})
    if 'ruleSetsForClient' in data:
        return data['ruleSetsForClient']
    return None


def graphql_get_ruleset(api_token: str, ruleset_name: str):
    """
    Get rulesets by their names

    :param api_token: the API token to access the GraphQL API
    :param ruleset_name: the name of the ruleset to fetch
    """
    if not ruleset_name:
        raise ValueError

    query = """
        {
          ruleSet(name: \"""" + ruleset_name + """\"){
            id
            name
            rules(howmany: 10000, skip: 0){
              id
              name
              content
              language
              ruleType
              pattern
              patternMultiline
              elementChecked
              tests {
                id
                name
                shouldFail
                content
                description
              }
            }
          }
        }"""
    data = do_graphql_query(api_token, {"query": query})
    if 'ruleSet' in data:
        return data['ruleSet']
    return None


