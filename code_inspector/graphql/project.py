"""
Function to create a file analysis using the GraphQL API.
"""

from code_inspector.graphql.common import do_graphql_query


def graphql_get_project_info(access_key: str, secret_key: str, project_name: str):
    """
    Get information about a project

    :param access_key access key to the API
    :param secret_key secret key to the API
    :param project_name: name of the project
    """
    if not project_name or not access_key or not secret_key:
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
    data = do_graphql_query(access_key, secret_key, {"query": query})
    if 'project' in data:
        return data['project']
    return None


def graphql_get_file_analysis(access_key: str, secret_key: str, file_analysis_id: int):
    """
    Get the file analysis object with violations

    :param access_key access key to the API
    :param secret_key secret key to the API
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
    return do_graphql_query(access_key, secret_key, {"query": query})
