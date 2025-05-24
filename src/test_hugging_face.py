import logging
from logs.config_logging import setup_logging
from config.config_yaml_loader import load_config
from utils.models import send_unique_prompt_gemini, get_sql_and_explanation, generate_prompt_for_test_hugging_face, send_unique_prompt_chatgpt
import pandas as pd
import time
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
TEMPERATURA = config.get("temperature")
TOP_P = config.get("top_p")
TIPO_PROMPT = config.get("tipo_prompt")
PROMPT_METHOD = config.get("prompt_method", "zero_shot").lower().strip()



NUM_PROMPTS = 500 #4018
VERSION = f"{PROMPT_METHOD}_{TIPO_PROMPT}_t{TEMPERATURA}_top{TOP_P}".replace(".","_")
BASE_PATH = os.path.join("data", "analytics", "Hugging_Face", MODELO).replace(".","_")

PATH_OUTPUT_FILE = (os.path.join(BASE_PATH, f"out_{MODELO}_{VERSION}")).replace(".","_") +".csv"


posicion_inicial = 0
df_hugging_face = pd.read_json("hf://datasets/b-mc2/sql-create-context/sql_create_context_v4.json")
df_hugging_face = df_hugging_face.iloc[posicion_inicial:NUM_PROMPTS].reset_index(drop=True)
sql_generados = []


logger.warning("----------------------------Start test------------------------------------")

logger.warning(f"LLM_MODEL: {LLM_MODEL}")
logger.warning(f"MODELO: {MODELO}")
logger.warning(f"TEMPERATURA: {TEMPERATURA}")
logger.warning(f"TOP_P: {TOP_P}")
logger.warning(f"TIPO_PROMPT: {TIPO_PROMPT}")
logger.warning(f"PROMPT_METHOD: {PROMPT_METHOD}")
logger.warning(f"Output file: {PATH_OUTPUT_FILE}")


try:
    for idx, row in df_hugging_face.iterrows():
        logger.warning(f"Processing row {idx+1}/{len(df_hugging_face)}")
        prompt = generate_prompt_for_test_hugging_face(row["question"], row["context"], SQL_MOTOR, TIPO_PROMPT)
        if LLM_MODEL == "gemini":
                response = send_unique_prompt_gemini(prompt)
        elif LLM_MODEL == "chatgpt":
                response = send_unique_prompt_chatgpt(prompt)
        sql_statement, explanation = get_sql_and_explanation(response)
        sql_generados.append(sql_statement)
        time.sleep(1) # to avoid rate limits

except Exception as e:
        logger.error(f"Error processing row {idx+1}: {e}")
finally:
        logger.warning("Finished processing.")
        df_hugging_face = df_hugging_face.head(len(sql_generados))
        df_hugging_face["sql_generado"] = sql_generados

        os.makedirs(BASE_PATH, exist_ok=True)
        time.sleep(2)

        df_hugging_face.to_csv(PATH_OUTPUT_FILE, index=False, sep="|")
        logger.warning("Results saved to resultado_in: " + PATH_OUTPUT_FILE)

logger.warning("----------------------------End test------------------------------------")
