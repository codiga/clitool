import yaml


def get_rulesets_from_codigafile(path: str):
    """
    Load the codiga.yml file
    :param path: the path to the file
    :return: the list of rulesets for the file
    """
    try:
        with open(path, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            if not data_loaded:
                return []
            if "rulesets" in data_loaded:
                return data_loaded["rulesets"]
            return []
        return []
    except (FileNotFoundError, yaml.scanner.ScannerError, yaml.YAMLError):
        logging.error("[get_rulesets_from_codigafile] invalid rosie file on %s", path)
        return []



def element_checked_api_to_json(value):
    """
    Mapped the element checked from the GraphQL type
    into a serializable data for the CLI
    :param value:
    :return:
    """
    if value is None:
        return None
    if value.lower() == "any":
        return "ANY"
    elif value.lower() == "assignment":
        return "ASSIGNMENT"
    elif value.lower() == "classdefinition":
        return "CLASS_DEFINITION"
    elif value.lower() == "forloop":
        return "FOR_LOOP"
    elif value.lower() == "functioncall":
        return "FUNCTION_CALL"
    elif value.lower() == "functiondefinition":
        return "FUNCTION_DEFINITION"
    elif value.lower() == "functionexpression":
        return "FUNCTION_EXPRESSION"
    elif value.lower() == "htmlelement":
        return "HTML_ELEMENT"
    elif value.lower() == "ifstatement":
        return "IF_STATEMENT"
    elif value.lower() == "interface":
        return "INTERFACE"
    elif value.lower() == "importstatement":
        return "IMPORT_STATEMENT"
    elif value.lower() == "variabledeclaration":
        return "VARIABLE_DECLARATION"
    elif value.lower() == "tryblock":
        return "TRY_BLOCK"
    elif value.lower() == "type":
        return "TYPE"
    return None
