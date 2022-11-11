import yaml

def get_rulesets_from_codigafile(path: str):
    try:
        with open(path, 'r') as stream:
            data_loaded = yaml.load(stream, Loader=yaml.BaseLoader)
            if not data_loaded:
                return []
            if "rulesets" in data_loaded:
                return data_loaded["rulesets"]
            return []
        return []
    except (FileNotFoundError, yaml.scanner.ScannerError, yaml.YAMLError):
        logging.error("[get_rulesets_from_codigafile] invalid rosie file on %s", path)
        return []
