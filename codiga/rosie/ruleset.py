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
