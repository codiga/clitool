import json
import requests
from typing import List

import yaml

from codiga.model.rosie_rule import RosieRule
from codiga.model.violation import Violation

ROSIE_URL = "https://analysis.codiga.io/analyze"

def analyze_rosie(filename: str, language: str, file_encoding: str, code_base64: str, rules: List[RosieRule]) -> List[Violation]:
    # data = {'key': 'value'}
    payload = {
        "filename": filename,
        "language": language.lower(),
        "fileEncoding": file_encoding,
        "codeBase64": code_base64,
        "rules": list(map(lambda x: x.to_json(), rules)),
        "logOutput": False
    }
    response = requests.post(ROSIE_URL, data=json.dumps(payload), headers={'Content-type': 'application/json'}, timeout=10)
    print(response.json())
    for rule_response in response['ruleResponses']:
        violations = rule_response['violations']
        
    return []
