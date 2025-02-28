# Desc: Utility functions for reading and querying data.
import pandas as pd
import pandasql as ps
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)


def read_data_and_definition(path: str, path_definition: str) -> pd.DataFrame:
    """
    Read data from a CSV file and definitions from another CSV file and return a DataFrame and markdown table.

    Args:
        path (str): The file path to the CSV data.
        path_definition (str): The file path to the CSV data field definitions.

    Returns:
        pd.DataFrame: The data read from the CSV file.
    """
    logger.debug("Attempting to read data from CSV file at path: " + path)
    try:
        df = read_data(path)
        df_definition_in_markdown = get_data_definition(path_definition)
        return df, df_definition_in_markdown
    except Exception as e:
        logger.error(f"Error reading data from {path}: {e}")
        raise

def read_data(path: str) -> pd.DataFrame:
    """
    Read data from a CSV file and return a DataFrame.

    Args:
        path (str): The file path to the CSV data.

    Returns:
        pd.DataFrame: The data read from the CSV file.
    """
    logger.debug("Attempting to read data from CSV file at path: " + path)
    try:
        df = pd.read_csv(path, header=0, delimiter=';', encoding="latin-1")
        logger.info("Data successfully read from " + path)
        return df
    except Exception as e:
        logger.error(f"Error reading data from {path}: {e}")
        raise

def query_data(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """
    Execute an SQL query on the given DataFrame using pandasql.

    Args:
        df (pd.DataFrame): The DataFrame to query.
        query (str): The SQL query string.

    Returns:
        pd.DataFrame: The result of the SQL query.
    """
    logger.debug("Executing SQL query: " + query)
    try:
        # Create an environment where the key 'df' maps to the provided DataFrame
        env = {"df": df}
        result_df = ps.sqldf(query, env)
        logger.info("SQL query executed successfully.")
        return result_df
    except Exception as e:
        logger.error(f"Error executing query '{query}': {e}")
        raise

def get_data_definition(path: str) -> str:
    """
    Read data from a CSV file containing data field definitions and return a DataFrame.

    Args:
        path (str): The file path to the CSV data field definitions.

    Returns:
        str: A markdown table containing the data field definitions.
    """
    logger.debug("Attempting to read data field definitions from CSV file at path: " + path)
    try:
        df_definition = read_data(path)
        markdown_table = df_definition.to_markdown(index=False)
        logger.info("Data field definitions successfully read from " + path)
        return markdown_table
    except Exception as e:
        logger.error(f"Error reading data field definitions from {path}: {e}")
        raise
