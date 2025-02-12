import os
import yaml
from typing import Any, Dict

def load_config() -> Dict[str, Any]:
    """
    Load the configuration from the `config.yaml` file located in the `config` subdirectory.

    Returns:
        Dict[str, Any]: 
            A dictionary containing the configuration data parsed from `config.yaml`.

    Raises:
        FileNotFoundError: 
            If the `config.yaml` file does not exist or cannot be found at the specified path.
        yaml.YAMLError: 
            If there is an error parsing the YAML file.
    """
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r", encoding="utf-8") as yaml_config_file:
        return yaml.safe_load(yaml_config_file)


