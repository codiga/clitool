import json
import requests
from typing import List

import yaml

from codiga.model.rosie_rule import RosieRule
from codiga.model.violation import Violation

ROSIE_URL = "https://analysis.codiga.io/analyze"

def analyze_rosie(filename: str, language: str, file_encoding: str, code_base64: str, rules: List[RosieRule]) -> List[Violation]:
    # data = {'key': 'value'}
    try:
        result = []
        payload = {
            "filename": filename,
            "language": language.lower(),
            "fileEncoding": file_encoding,
            "codeBase64": code_base64,
            "rules": list(map(lambda x: x.to_json(), rules)),
            "logOutput": False
        }
        response = requests.post(ROSIE_URL, data=json.dumps(payload), headers={'Content-type': 'application/json'}, timeout=10)
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
    except TimeoutError:
        return []
