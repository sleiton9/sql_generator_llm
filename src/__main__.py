import logging
from logs.config_logging import setup_logging
from config.config_yaml_loader import load_config
from utils.models import send_prompt
from utils.data import read_data, query_data

# Setup the logs
setup_logging()
logger = logging.getLogger(__name__)

# Load configuration settings from a YAML file.
config = load_config()
PATH_RAW_DATA = config.get("paths", {}).get("raw_data")


def main() -> None:
    """
    Main function to test the Gemini API connection by sending a sample prompt.
    """
    try:
        logger.info("----------------------------Start main function------------------------------------")

        test_prompt = "Tengo dos perros en mi casa"
        response = send_prompt(test_prompt)

        test_prompt = "Cuentos perros tengo en mi casa?"
        response = send_prompt(test_prompt)

        df = read_data(PATH_RAW_DATA)

        df = query_data(df, "SELECT * FROM df WHERE PESO > 1000")
        print(df)

        logger.info("----------------------------End main function--------------------------------------")
    except Exception as e:
        logger.error(e)
        raise


if __name__ == "__main__":
    main()

