import logging
import os
import requests
import requests.exceptions
from typing import List



from codiga.model.rosie_rule import RosieRule
from codiga.model.violation import Violation

ROSIE_URL = "https://analysis.codiga.io/analyze"

log: logging.Logger = logging.getLogger('codiga')

def analyze_rosie(filename: str, language: str, file_encoding: str, code_base64: str, rules: List[RosieRule]) -> List[Violation]:
    """
    Run an analysis with rosie
    :param filename: the filename to send
    :param language: the language to use
    :param file_encoding: the file encoding
    :param code_base64: the code encoded in base64
    :param rules: the list of rules to use
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
            "logOutput": False
        }
        response = requests.post(ROSIE_URL, json=payload, headers={'Content-type': 'application/json'}, timeout=10)
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
