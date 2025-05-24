import logging
from logs.config_logging import setup_logging
from config.config_yaml_loader import load_config
from utils.models import send_prompt, get_sql_and_explanation, generate_initial_prompt, generate_question_prompt, initialize_gemini_rag, get_relevant_context_gemini
from utils.data import read_data_and_definition, query_data

# Setup the logs
setup_logging()
logger = logging.getLogger(__name__)

# Load configuration settings from a YAML file.
config = load_config()
PROMPT_METHOD = config.get("prompt_method")
PATH_RAW_DATA = config.get("paths", {}).get("raw_data")
PATH_RAW_DATA_DEFINITION = config.get("paths", {}).get("raw_data_definition")
SQL_MOTOR = config.get("sql_motor")
TABLE_NAME = config.get("table_name")
THRESHOLD_SIMILARITY_RAG = config.get("threshold_similarity_rag")
LLM_MODEL = config.get("llm_model", "gemini").lower().strip()
if LLM_MODEL == "gemini":
      MODELO = config.get("gemini_model").lower().strip()
elif LLM_MODEL == "chatgpt":
      MODELO = config.get("chatgpt_model").lower().strip()


def main() -> None:
    """
    Main function to test the Gemini API connection by sending a sample prompt.
    """
    try:
        logger.info("----------------------------Start main function------------------------------------")
        logger.info("LLM Model: " + LLM_MODEL)
        logger.info("Model: " + MODELO)
        logger.info("Prompt method: " + PROMPT_METHOD)

        df, str_full_context = read_data_and_definition(PATH_RAW_DATA, PATH_RAW_DATA_DEFINITION)

        print("Puedes realizar varias preguntas relacionada a los datos, Escribir 'exit' para salir.")
        prompt = generate_initial_prompt(str_full_context, SQL_MOTOR, TABLE_NAME)
        send_prompt(prompt)

        if PROMPT_METHOD == "rag":
            vector_store = initialize_gemini_rag()

        while True:
            user_question = input("¿Cuál es tu duda frente a los datos? \n")
            if user_question.lower().lstrip() == "exit":
                logger.info("----------------------------End main function--------------------------------------")
                break
            
            context = None
            if PROMPT_METHOD == "rag":
                results = get_relevant_context_gemini(user_question,
                                        vector_store,
                                        threshold=THRESHOLD_SIMILARITY_RAG)
                context = [item['metadata'] for item in results]

            prompt = generate_question_prompt(user_question, context)
            response = send_prompt(prompt)
            sql_statement, explanation = get_sql_and_explanation(response)

            if sql_statement is None:
                print("La pregunta no está relacionada con los datos o no se pudo generar una consulta.")
                print("Explicación: ", explanation)
            else:
                try:
                    df_result = query_data(df, sql_statement)
                    print("Explicación:", explanation)
                    print("Resultado de la pregunta:")
                    print(df_result)
                except Exception as e:
                    print("Error al ejecutar la consulta SQL:", e)
                    print("Explicación:", explanation)

        
    except Exception as e:
        logger.error(e)
        raise


if __name__ == "__main__":
    main()

# Cual es el cliente que mas vendio en agosto de 2024? agregar el total de ventas
# Cual es el codigo cliente que mas vendio en agosto de 2024? agregar el total de ventas
# cual es el top 5 de ciudades que tienen mayor valor de ventas y cual es el total de ventas? 
# cual es el top 5 de ciudades que tienen mayor conteo de ventas y cual es ese numero de ventas?
# Cual es el cliente con mayor ventas en la cidudad AzAwNyk/KH8= en el 2024?
