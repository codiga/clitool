"""
Function to create a file analysis using the GraphQL API.
"""

from codiga.graphql.common import do_graphql_query


def graphql_get_project_info(api_token: str, project_name: str):
    """
    Get information about a project

    :param api_token: the API token to access the GraphQL API
    :param project_name: name of the project
    """
    if not project_name or not api_token:
        raise ValueError
    query = """
        {
          project(name:\"""" + project_name + """\") {
            id
            name
            public
            description
            status
            owner{
              username
            }
            level
            analysesCount
          }
        }
    """
    data = do_graphql_query(api_token, {"query": query})
    if 'project' in data:
        return data['project']
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
