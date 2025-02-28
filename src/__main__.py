import logging
from logs.config_logging import setup_logging
from config.config_yaml_loader import load_config
from utils.models import send_prompt, get_sql_and_explanation
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
        logger.info("----------------------------Start main function------------------------------------")

        df, definition_df = read_data_and_definition(PATH_RAW_DATA, PATH_RAW_DATA_DEFINITION)

        user_question = input("¿Cuál es tu duda frente a los datos? ")


        test_prompt = f"""
                            El usuario te hará una pregunta en lenguaje natural y tu salida debe ser
                            un objeto JSON con dos claves:
                            1) "sql_statement": que contenga la sentencia SQL necesaria (sin explicaciones internas).
                            2) "explanation": que describa en lenguaje natural cómo interpretar o usar el resultado, agregando las columnas de la fuente y las agregaciones usadas
                                de la consulta (sin mencionar directamente que se genera un SQL internamente para generar el resultado). 
                                Si la pregunta NO está relacionada con la tabla o los datos, entonces:
                                    - "sql_statement": null
                                    - "explanation": "La pregunta no está relacionada con los datos."

                            El motor SQL será: {SQL_MOTOR}
                            El nombre de la tabla es: {TABLE_NAME}

                            Este es el contexto de la base de datos en la cual se debe basar la consulta:
                            {definition_df}

                            La pregunta del usuario es: {user_question}

                            Por favor, devuelve la respuesta exclusivamente en un bloque de código delimitado por triple
                            backticks ``` con formato JSON válido, sin markdown, que tenga estas dos claves:
                            "sql_statement" y "explanation".
                        """
        response = send_prompt(test_prompt)

        sql_statement, explanation = get_sql_and_explanation(response)

        if sql_statement is None:
            print("La pregunta no está relacionada con los datos o no se pudo generar consulta SQL.")
            print("Explicación:", explanation)
        else:
            print("Explicación:", explanation)
            df_result = query_data(df, sql_statement)
            print("Resultado de la pregunta:")
            print(df_result)

        logger.info("----------------------------End main function--------------------------------------")
    except Exception as e:
        logger.error(e)
        raise


if __name__ == "__main__":
    main()

# Cual es el cliente que mas vendio en agosto de 2024? agregar el total de ventas
# Cual es el codigo cliente que mas vendio en agosto de 2024? agregar el total de ventas
# cual es el top 5 de ciudades que tienen mayor valor de ventas y cual es el total de ventas? 
# cual es el top 5 de ciudades que tienen mayor conteo de ventas y cual es ese numero de ventas?
