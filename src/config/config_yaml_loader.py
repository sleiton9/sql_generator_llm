import os
import yaml
from typing import Any, Dict


def load_config() -> Dict[str, Any]:
    """
    Load configuration from the config.yaml file and add dynamic paths
    based on the project folder structure.

    Returns:
        Dict[str, Any]: A dictionary containing the configuration data and additional path settings.

    Raises:
        FileNotFoundError: If the config.yaml file is not found.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """
    # Path to the config.yaml file, assumed to be in the same directory as this script
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

    with open(config_path, "r", encoding="utf-8") as yaml_config_file:
        config = yaml.safe_load(yaml_config_file)

    # Determine the project root (two levels up from this script)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # Add a 'paths' section to the configuration dictionary
    config["paths"] = {
        "project_root": project_root,
        "raw_data": os.path.join(
            project_root, "data", "raw", "data_micaja_ofuscada_20250214.csv"
        ),
        # Additional paths can be added here
    }

    return config
