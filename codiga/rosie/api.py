import logging
import os
import time

import requests
import requests.exceptions
from typing import List



from codiga.model.rosie_rule import RosieRule
from codiga.model.violation import Violation

ROSIE_URL = "https://analysis.codiga.io/analyze"

log: logging.Logger = logging.getLogger('codiga')


def analyze_rosie(filename: str, language: str, file_encoding: str,
                  code_base64: str, rules: List[RosieRule],
                  server_url: str = ROSIE_URL) -> List[Violation]:
    """
    Run an analysis with rosie
    :param filename: the filename to send
    :param language: the language to use
    :param file_encoding: the file encoding
    :param code_base64: the code encoded in base64
    :param rules: the list of rules to use
    :param server_url: the URL of the Rosie server
    :return: the list of violations
    """
    try:
        result = []
        payload = {
            "filename": os.path.basename(filename),
            "language": language.lower(),
            "fileEncoding": file_encoding,
            "codeBase64": code_base64,
            "rules": list(map(lambda x: x.to_json(), rules)),
            "logOutput": False,
            "options": {
                "useTreeSitter": True,
                "logOutput": False
            }
        }
        start_ts = time.time()
        response = requests.post(server_url, json=payload, headers={'Content-type': 'application/json'}, timeout=10)
        stop_ts = time.time()
        try:
            response_json = response.json()
            for rule_response in response_json['ruleResponses']:
                violation_name = rule_response['identifier']
                violations = rule_response['violations']
                for rosie_violation in violations:
                    new_violation = Violation(
                        id=violation_name,
                        line=int(rosie_violation['start']['line']),
                        description=rosie_violation['message'],
                        severity=rosie_violation['severity'],
                        category=rosie_violation['category'],
                        language=language,
                        tool="codiga",
                        rule=violation_name
                    )
                    result.append(new_violation)
            return result
        except requests.exceptions.JSONDecodeError:
            log.error("error while decoding analysis output: %s", response.text)
            return []
    except (TimeoutError, requests.exceptions.ReadTimeout):
        log.error("timeout when processing file %s", filename)
        return []
