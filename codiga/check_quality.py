"""Check the quality of a project for a given SHA. This tool is used to integrate Codiga
with Continuous Integration Pipelines.

Usage:
    codiga-check-quality [options]


Global options:
    --sha <sha>                           SHA to analyze (required)
    --project <project-name>              Project name to use (required)
    --min-quality-score <score>           Code Quality Score from 0 to 100 (optional)
    --min-quality-grade <grade>           Minimum Code Grade EXCELLENT, GOOD, NEUTRAL, WARNING, CRITICAL (optional)
    --max-defects-rate <rate>             Max rate of defect per sloc (optional)
    --max-complex-functions-rate <rate>   Max rate of complex functions in the total number of functions (optional)
    --max-long-functions-rate <rate>      Max rate of long functions in the total number of functions (optional)
    --max-timeout-sec <timeout>           Maximum time to wait before the analysis is done (in secs). Default to 600.
Example:
    $ codiga-check-quality --project "MY SUPER PROJECT" --min-quality-score 90 --sha 7644598cb436840a3961dd2b66172c18a2ff7823
"""

import os
import json
import logging
import sys
import time

import docopt
from codiga.common import is_grade_lower
from codiga.constants import DEFAULT_TIMEOUT, API_TOKEN_ENVIRONMENT_VARIABLE

from .graphql.common import do_graphql_query
from .version import __version__

logging.basicConfig()

log = logging.getLogger('codiga')


def get_analysis_by_revision(api_token, project_name, revision):
    """
    Get an analysis using its ID
    :param api_token: token to poll the API
    :param project_name: name of the project to analyze
    :param revision: the revision to analyze
    :return: the return code depending on the results or some processing error
    """

    query = """
        {
            project(name: \"""" + project_name + """\") {
              analyses(revision: \"""" + revision + """\", howmany: 1, skip: 0) {
                id
                status
                slocs
                techdebt{
                  grade
                  score
                }
                summary{
                  duplicates
                  violations
                  duplicated_lines
                  longFunctions
                  totalFunctions
                  complexFunctions
                }
              }
            }
        }
        """
    response_json = do_graphql_query(api_token, {"query": query})
    logging.info("Analysis response %s", response_json)
    return response_json['project']


def main(argv=None):
    """
    Main function that makes the magic happen.
    :param argv:
    :return:
    """
    options = docopt.docopt(__doc__, argv=argv, version=__version__)
    sha = options['--sha']
    project_name = options['--project']
    min_quality_score_argument = options['--min-quality-score']
    min_quality_grade_argument = options['--min-quality-grade']
    max_defects_rate_argument = options['--max-defects-rate']
    max_complex_functions_rate_argument = options['--max-complex-functions-rate']
    max_long_functions_rate_argument = options['--max-long-functions-rate']
    custom_timeout_sec = options['--max-timeout-sec']

    try:
        timeout = int(custom_timeout_sec) if custom_timeout_sec is not None else DEFAULT_TIMEOUT
    except ValueError:
        timeout = DEFAULT_TIMEOUT

    if timeout == 0:
        timeout = DEFAULT_TIMEOUT

    log.addHandler(logging.StreamHandler())

    log.setLevel(logging.INFO)

    log.info("Invoking codiga-check-quality with the following parameters")
    log.info("                    (parameters)                    ")
    log.info("sha: %s", sha)
    log.info("project_name: %s", project_name)
    log.info("min_quality_score_argument: %s", min_quality_score_argument)
    log.info("min_quality_grade_argument: %s", min_quality_grade_argument)
    log.info("max_defects_rate_argument: %s", max_defects_rate_argument)
    log.info("max_complex_functions_rate_argument: %s", max_complex_functions_rate_argument)
    log.info("max_long_functions_rate_argument: %s", max_long_functions_rate_argument)
    log.info("custom_timeout_sec: %s", custom_timeout_sec)
    log.info("                      (starting)                    ")

    try:
        api_token = os.environ.get(API_TOKEN_ENVIRONMENT_VARIABLE)

        if not api_token:
            log.info('%s environment variable not defined!', API_TOKEN_ENVIRONMENT_VARIABLE)
            sys.exit(1)

        if not project_name:
            log.info('Project name not defined')
            sys.exit(1)

        if not sha:
            log.info('GitHub SHA required')
            sys.exit(1)

        # Filter argument and bad values.
        if min_quality_score_argument is not None:
            min_quality_score = int(min_quality_score_argument)
        else:
            min_quality_score = None

        if max_defects_rate_argument is not None:
            max_defects_rate = float(max_defects_rate_argument)
        else:
            max_defects_rate = None

        if max_complex_functions_rate_argument is not None:
            max_complex_functions_rate = float(max_complex_functions_rate_argument)
        else:
            max_complex_functions_rate = None

        if max_long_functions_rate_argument is not None:
            max_long_functions_rate = float(max_long_functions_rate_argument)
        else:
            max_long_functions_rate = None

        deadline = time.time() + timeout

        while True:
            now = time.time()
            if now > deadline:
                log.error("Deadline expired")
                sys.exit(1)

            poll_analysis = None
            project = get_analysis_by_revision(api_token, project_name, sha)
            analysis_complete = False
            if project['analyses'] and len(project['analyses']) > 0:
                poll_analysis = project['analyses'][0]
                status = poll_analysis['status']
                if status.upper() in ["DONE", "ERROR", "SAME_REVISION"]:
                    poll_analysis = project['analyses'][0]
                    analysis_complete = True
            if not analysis_complete:
                log.debug("analysis not completed yet")
                time.sleep(5)
                continue

            print(json.dumps(poll_analysis, indent=4))

            analysis_slocs = int(poll_analysis['slocs'])
            analysis_violations = int(poll_analysis['summary']['violations'])
            analysis_complex_functions = int(poll_analysis['summary']['complexFunctions'])
            analysis_long_functions = int(poll_analysis['summary']['longFunctions'])
            analysis_total_functions = int(poll_analysis['summary']['totalFunctions'])
            analysis_score = poll_analysis['techdebt']['score']
            analysis_grade = poll_analysis['techdebt']['grade']

            if analysis_slocs > 0:
                if analysis_total_functions > 0:
                    analysis_complex_function_rate = analysis_complex_functions / analysis_total_functions
                    analysis_long_function_rate = analysis_long_functions / analysis_total_functions
                else:
                    analysis_complex_function_rate = 0
                    analysis_long_function_rate = 0

                analysis_violations_rate = analysis_violations / analysis_slocs
            else:
                analysis_complex_function_rate = 0
                analysis_long_function_rate = 0
                analysis_violations_rate = 0

            logging.info("analysis_score: %s", analysis_score)
            logging.info("analysis_grade: %s", analysis_grade)
            logging.info("analysis_violations_rate: %s", analysis_violations_rate)
            logging.info("analysis_complex_function_rate: %s", analysis_complex_function_rate)
            logging.info("analysis_long_function_rate: %s", analysis_long_function_rate)

            if analysis_score and min_quality_score is not None and analysis_score < min_quality_score:
                log.info("analysis score %s is lower than minimum expected score %s", analysis_score, min_quality_score)
                sys.exit(1)

            if max_complex_functions_rate is not None and analysis_complex_function_rate > max_complex_functions_rate:
                log.info("complex function rate %s is higher than maximum %s", analysis_complex_function_rate, max_complex_functions_rate)
                sys.exit(1)

            if max_long_functions_rate is not None and analysis_long_function_rate > max_long_functions_rate:
                log.info("long function rate %s is higher than maximum %s", analysis_long_function_rate, max_long_functions_rate)
                sys.exit(1)

            if max_defects_rate is not None and analysis_violations_rate > max_defects_rate:
                log.info("violation rate %s is higher than maximum %s", analysis_violations_rate, max_defects_rate)
                sys.exit(1)

            if min_quality_grade_argument is not None and is_grade_lower(analysis_grade, min_quality_grade_argument):
                log.info("grade %s is lower than grade %s", analysis_grade, min_quality_grade_argument)
                sys.exit(1)

            log.info("Everything is fine, all conditions passed")
            sys.exit(0)

        sys.exit(0)
    except KeyboardInterrupt:  # pragma: no cover
        log.info('Aborted')
        sys.exit(1)
    sys.exit(0)
