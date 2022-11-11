import typing
from dataclasses import dataclass


@dataclass
class RosieRule:
    id: str
    content_base64: str
    language: str
    rule_type: str
    entity_checked: typing.Optional[str]
    pattern: typing.Optional[str]

    def to_json(self):
        return {
            "id": self.id,
            "contentBase64": self.content_base64,
            "language": self.language,
            "type": self.rule_type,
            "entityChecked": self.entity_checked,
            "pattern": self.pattern
        }


ELEMENT_CHECKED_TO_ENTITY_CHECKED: typing.Dict[str, str] = {
    "FunctionCall": "functioncall",
    "IfCondition": "ifcondition",
    "Import": "import",
    "Assignment": "assign",
    "ForLoop": "forloop",
    "FunctionDefinition": "functiondefinition",
    "TryBlock": "tryblock"
}


def convert_rules_to_rosie_rules(rulesets_api) -> typing.List[RosieRule]:
    rules = []
    for ruleset in rulesets_api:
        ruleset_name = ruleset['name']

        for rule in ruleset['rules']:
            rule_name = f"{ruleset_name}/{rule['name']}"
            rule_content = rule['content']
            language = rule['language'].lower()
            rule_type = rule['ruleType'].lower()
            pattern = rule['pattern']

            if rule_type == "ast":
                entity_checked = ELEMENT_CHECKED_TO_ENTITY_CHECKED.get(rule['elementChecked'])
            else:
                entity_checked = None

            if rule_type == "ast" and not entity_checked:
                continue

            rosie_rule = RosieRule(id=rule_name,
                                   content_base64=rule_content,
                                   language=language,
                                   rule_type=rule_type,
                                   entity_checked=entity_checked,
                                   pattern=pattern)
            rules.append(rosie_rule)
    return rules
