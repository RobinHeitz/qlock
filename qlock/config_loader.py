import yaml







def load_config(path):
    """Loads yaml config file.
    
    Params:
    - path (str): Path to yaml file."""

    with open(path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return {}
    
    return config