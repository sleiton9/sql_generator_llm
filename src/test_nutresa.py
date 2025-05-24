import logging
from logs.config_logging import setup_logging
from config.config_yaml_loader import load_config
from utils.models import send_unique_prompt_gemini, get_sql_and_explanation, generate_prompt_for_test_nutresa, send_unique_prompt_chatgpt, initialize_gemini_rag, get_relevant_context_gemini
from utils.data import read_data_and_definition
import pandas as pd
import time
import pandasql as ps
import os

# Setup the logs
setup_logging()
logger = logging.getLogger(__name__)

# Load configuration settings from a YAML file.
config = load_config()
SQL_MOTOR = config.get("sql_motor")
LLM_MODEL = config.get("llm_model", "gemini").lower().strip()
if LLM_MODEL == "gemini":
      MODELO = config.get("gemini_model").lower().strip()
elif LLM_MODEL == "chatgpt":
      MODELO = config.get("chatgpt_model").lower().strip()
PROMPT_METHOD = config.get("prompt_method").lower().strip()
PATH_RAW_DATA = config.get("paths", {}).get("raw_data")
PATH_RAW_DATA_DEFINITION = config.get("paths", {}).get("raw_data_definition")
THRESHOLD_SIMILARITY_RAG = config.get("threshold_similarity_rag")
TIPO_PROMPT = config.get("tipo_prompt")
TABLE_NAME = config.get("table_name")



VERSION = f"{PROMPT_METHOD}_{TIPO_PROMPT}".replace(".","_")
BASE_PATH = os.path.join("data", "analytics", "Nutresa", MODELO).replace(".","_")
PATH_OUTPUT_FILE = (os.path.join(BASE_PATH, f"out_{VERSION}")).replace(".","_") +".csv"

path_input_nutresa = os.path.join("data", "stage", "consultas_nutresa_resueltas.csv")
df_preguntas_nutresa = pd.read_csv(path_input_nutresa, sep="\t", encoding="latin-1") 

df_data_nutresa, context = read_data_and_definition(PATH_RAW_DATA, PATH_RAW_DATA_DEFINITION)
sql_generados = []
logger.warning("----------------------------Start test------------------------------------")

logger.warning("LLM Model: " + LLM_MODEL)
logger.warning("Model: " + MODELO)
logger.warning("Prompt method: " + PROMPT_METHOD)
logger.warning("Tipo prompt: " + TIPO_PROMPT)

if PROMPT_METHOD == "rag":
    vector_store = initialize_gemini_rag()


def ejecutar_sql_pandasql(row):
    """Ejecuta la sentencia SQL de una fila usando pandasql y registra el resultado o el error."""
    try:
        sentencia_sql = row['sql_generado_llm']
        # Definir un entorno global para que pandasql acceda al DataFrame 'df'
        env = {"df": df_data_nutresa}
        resultado = ps.sqldf(sentencia_sql, env)
        return resultado.to_dict('records')  # Convertir el DataFrame resultante a una lista de diccionarios
    except Exception as e:
        return str(e).replace("\t", " ")  # Devolver el error como cadena

try:
    for idx, row in df_preguntas_nutresa.iterrows():
        logger.warning(f"Processing row {idx+1}/{len(df_preguntas_nutresa)}")
        if PROMPT_METHOD == "rag":
            results = get_relevant_context_gemini(row["Pregunta"],
                                    vector_store,
                                    threshold=THRESHOLD_SIMILARITY_RAG)
            context = [item['metadata'] for item in results]
        prompt = generate_prompt_for_test_nutresa(row["Pregunta"], context, SQL_MOTOR, TIPO_PROMPT, TABLE_NAME)
        if LLM_MODEL == "gemini":
                response = send_unique_prompt_gemini(prompt)
        elif LLM_MODEL == "chatgpt":
                response = send_unique_prompt_chatgpt(prompt)
        sql_statement, explanation = get_sql_and_explanation(response)
        sql_generados.append(sql_statement)
        time.sleep(1)

except Exception as e:
        logger.error(f"Error processing row {idx+1}: {e}")
finally:
        logger.warning("Finished processing.")
        df_preguntas_nutresa = df_preguntas_nutresa.head(len(sql_generados))
        df_preguntas_nutresa["sql_generado_llm"] = sql_generados

        os.makedirs(BASE_PATH, exist_ok=True)
        time.sleep(2)

        df_preguntas_nutresa['resultado_sql_generado_llm'] = df_preguntas_nutresa.apply(ejecutar_sql_pandasql, axis=1)

        df_preguntas_nutresa.to_csv(PATH_OUTPUT_FILE, index=False, sep="|", encoding="latin-1")
        logger.warning("Results saved to resultado_in: " + PATH_OUTPUT_FILE)

logger.warning("----------------------------End test------------------------------------")
