# Desc: Utility functions for reading and querying data.
import pandas as pd
import pandasql as ps
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)


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
        df = pd.read_csv(path, header=0, delimiter=';')
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
