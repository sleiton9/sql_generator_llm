# Desc: Utility functions for reading and querying data.
import pandas as pd
import pandasql as ps
import logging
import json
import os
from datetime import datetime
import csv

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
        str: A markdown table containing the data field definitions.
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
    Read data from a CSV file containing data field definitions and return a markdown table.

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

def read_json(path: str) -> dict | None:
    """
    Reads and parses a JSON file.

    Args:
        path: The path to the JSON file.

    Returns:
        A dictionary with the parsed JSON data, or None if an error occurs.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"JSON file read successfully from {path}")
        return data
    except FileNotFoundError:
        logger.error(f"Error: JSON file not found at path: {path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Error: JSON file at {path} is not valid JSON.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error reading JSON file: {e}")
        return None

def save_query_result(user_question: str, sql_statement: str, explanation: str, result: str = None) -> None:
    """
    Guarda el resultado de una consulta en un archivo CSV.
    
    Args:
        user_question (str): La pregunta del usuario
        sql_statement (str): La consulta SQL generada
        explanation (str): La explicación generada
        result (str): El resultado de la consulta (opcional)
    """
    try:
        # Crear directorio de resultados si no existe
        results_dir = os.path.join("data", "analytics", "user_queries")
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_path = os.path.join(results_dir, "consultas_guardadas.csv")
        
        # Verificar si el archivo existe para escribir encabezados
        file_exists = os.path.isfile(file_path)
        
        with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'pregunta', 'sql_generado', 'explicacion', 'resultado']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
            
            # Escribir encabezados solo si es un archivo nuevo
            if not file_exists:
                writer.writeheader()
            
            # Preparar el resultado para guardado
            result_str = str(result) if result is not None else "No ejecutado"
            
            writer.writerow({
                'timestamp': timestamp,
                'pregunta': user_question,
                'sql_generado': sql_statement if sql_statement else "No generado",
                'explicacion': explanation if explanation else "No disponible",
                'resultado': result_str
            })
        
        print(f"✅ Consulta guardada exitosamente en: {file_path}")
        logger.info(f"Query saved successfully to: {file_path}")
        
    except Exception as e:
        print(f"❌ Error al guardar la consulta: {e}")
        logger.error(f"Error saving query: {e}")

def ask_user_to_save() -> bool:
    """
    Pregunta al usuario si quiere guardar el resultado.
    
    Returns:
        bool: True si quiere guardar, False si no
    """
    while True:
        save_choice = input("\n¿Deseas guardar esta consulta y su resultado? (s/n): ").lower().strip()
        
        if save_choice in ['s', 'si', 'sí', 'y', 'yes']:
            return True
        
        elif save_choice in ['n', 'no']:
            return False
        
        else:
            print("Por favor, responde 's' para sí o 'n' para no")
