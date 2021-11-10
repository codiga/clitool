"""
Function to create a file analysis using the GraphQL API.
"""
import json

from codiga.graphql.common import do_graphql_query


def graphql_create_file_analysis(api_token: str, filename: str,
                                 language: str, content: str, project_id: int) -> int:
    """
    Create a file analysis and return its identifier.

    :param api_token: the API token to access the GraphQL API
    :param filename: filename to analyze
    :param language: language of the file
    :param content: content of the file
    :param project_id: project identifier
    :return: the file analysis identifier
    """
    if not filename or not language or not content:
        raise ValueError
    code_content = json.dumps(content)
    project_id_text: str = "null"
    if project_id:
        project_id_text = str(project_id)
    query = """
    mutation{
        createFileAnalysis (
            language: """ + language + """,
            code: """ + code_content + """,
            filename: \"""" + filename + """\"
            projectId: """ + project_id_text + """
        )
    }
    """
    data = do_graphql_query(api_token, {"query": query})
    return int(data['createFileAnalysis'])


def graphql_get_file_analysis(api_token: str, file_analysis_id: int):
    """
    Get the file analysis object with violations

    :param api_token: the API token to access the GraphQL API
    :param file_analysis_id: the identifier of the file analysis to get
    :return: the file analysis object and it's violations
    """
    if not api_token or not file_analysis_id:
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
    data = do_graphql_query(api_token, {"query": query})
    return data
