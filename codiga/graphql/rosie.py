import typing
"""
All the GraphQL queries for Rosie
"""

from codiga.graphql.common import do_graphql_query


def get_rulesets(api_token: str, ruleset_names: typing.List[str]):
    return list(map(lambda x: get_ruleset(api_token, x), ruleset_names))


def get_ruleset(api_token: str, ruleset_name: str):
    """
    Get a ruleset by its name

    :param api_token: the API token to access the GraphQL API
    :param ruleset_name: the name of all ruleset to fetch
    """
    if not ruleset_name or not api_token:
        raise ValueError
    query = """
        {
            ruleSet(name: \""""+ruleset_name+"""\"){
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
            }
          }
        }
    """
    data = do_graphql_query(api_token, {"query": query})
    if 'ruleSet' in data:
        return data['ruleSet']
    return None


def graphql_get_file_analysis(api_token: str, file_analysis_id: int):
    """
    Get the file analysis object with violations

    :param api_token: the API token to access the GraphQL API
    :param file_analysis_id: the identifier of the file analysis to get
    :return: the file analysis object and it's violations
    """
    if not file_analysis_id:
        raise ValueError

    query = """
    {
      getFileAnalysis(id:""" + str(file_analysis_id) + """){
        status
        filename
        language
        runningTimeSeconds
        timestamp
        violations {
          id
          language
          description
          severity
          category
          line
          lineCount
          tool
          rule
          ruleUrl
        }
      }
    }
    """
    return do_graphql_query(api_token, {"query": query})
