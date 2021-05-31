"""
Function to create a file analysis using the GraphQL API.
"""
from code_inspector.graphql.common import do_graphql_query


def graphql_create_file_analysis(filename: str, language: str, content: str, project_id: int) -> int:
    """
    Create a file analysis and return its identifier.

    :param filename: filename to analyze
    :param language: language of the file
    :param content: content of the file
    :param project_id: project identifier
    :return: the file analysis identifier
    """
    if not filename or not language or not content:
        raise ValueError
    query = """
    mutation{
        createFileAnalysis (
            language: """ + language + """,
            code: \"""" + content + """\",
            filename: \"""" + filename + """\"
            projectId: """ + project_id if project_id else "null" + """\"
        )
    }
    """
    data = do_graphql_query(query)
    return int(data['createFileAnalysis'])


def graphql_get_file_analysis(file_analysis_id: int):
    """
    Get the file analysis object with violations
    :param file_analysis_id: the identifier of the file analysis to get
    :return: the file analysis object and it's violations
    """
    if not file_analysis_id:
        raise ValueError

    query = """
    {
      getFileAnalysis(id:""" + file_analysis_id + """){
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
    return do_graphql_query(query)
