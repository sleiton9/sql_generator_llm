import logging
from logs.config_logging import setup_logging
from config.config_yaml_loader import load_config
from utils.models import send_prompt, get_sql_and_explanation, generate_prompt
from utils.data import read_data_and_definition, query_data

# Setup the logs
setup_logging()
logger = logging.getLogger(__name__)

# Load configuration settings from a YAML file.
config = load_config()
PATH_RAW_DATA = config.get("paths", {}).get("raw_data")
PATH_RAW_DATA_DEFINITION = config.get("paths", {}).get("raw_data_definition")
SQL_MOTOR = config.get("sql_motor")
TABLE_NAME = config.get("table_name")


def main() -> None:
    """
    Main function to test the Gemini API connection by sending a sample prompt.
    """
    try:
        df, definition_df = read_data_and_definition(PATH_RAW_DATA, PATH_RAW_DATA_DEFINITION)

        print("Puedes realizar varias preguntas relacionada a los datos, Escribir 'exit' para salir.")
        while True:
            logger.info("----------------------------Start main function------------------------------------")


            user_question = input("¿Cuál es tu duda frente a los datos? ")
            if user_question.lower().lstrip() == "exit":
                logger.info("----------------------------End main function--------------------------------------")
                break

            prompt = generate_prompt(user_question, definition_df, SQL_MOTOR, TABLE_NAME)
            response = send_prompt(prompt)
            sql_statement, explanation = get_sql_and_explanation(response)

            if sql_statement is None:
                print("La pregunta no está relacionada con los datos o no se pudo generar una consulta.")
                print("Explicación:", explanation)
            else:
                df_result = query_data(df, sql_statement)
                print("Explicación:", explanation)
                print("Resultado de la pregunta:")
                print(df_result)

        
    except Exception as e:
        logger.error(e)
        raise


if __name__ == "__main__":
    main()

# Cual es el cliente que mas vendio en agosto de 2024? agregar el total de ventas
# Cual es el codigo cliente que mas vendio en agosto de 2024? agregar el total de ventas
# cual es el top 5 de ciudades que tienen mayor valor de ventas y cual es el total de ventas? 
# cual es el top 5 de ciudades que tienen mayor conteo de ventas y cual es ese numero de ventas?
