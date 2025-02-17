"""
This module connects to the Gemini API using the Google genai client,
sends a prompt to the model, and prints the generated response.
"""
import logging
from logs.config_logging import setup_logging
from config.config_yaml_loader import load_config
from utils.models import send_prompt

# Load configuration settings from a YAML file.
config = load_config()

# Setup the logs
setup_logging()
logger = logging.getLogger(__name__)



def main() -> None:
    """
    Main function to test the Gemini API connection by sending a sample prompt.
    """
    logger.info("----------------------------Start main function------------------------------------")

    test_prompt = "Tengo dos perros en mi casa"
    response = send_prompt(test_prompt)

    test_prompt = "Cuentos perros tengo en mi casa?"
    response = send_prompt(test_prompt)

    logger.info("----------------------------End main function--------------------------------------")



if __name__ == "__main__":
    main()

