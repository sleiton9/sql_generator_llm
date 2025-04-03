import logging
from logs.config_logging import setup_logging
from config.config_yaml_loader import load_config
from utils.models import send_prompt, get_sql_and_explanation, generate_prompt_for_test
import pandas as pd
import time
import os

# Setup the logs
setup_logging()
logger = logging.getLogger(__name__)

# Load configuration settings from a YAML file.
config = load_config()
SQL_MOTOR = config.get("sql_motor")
PATH_OUTPUT_FILE = os.path.join("src","testing", "gemini-20-flash", "sql_generados_gemini_20.csv")


df_hugging_face = pd.read_json("hf://datasets/b-mc2/sql-create-context/sql_create_context_v4.json")
df_hugging_face = df_hugging_face.iloc[:390]
sql_generados = []


logger.warning("----------------------------Start test------------------------------------")

try:
    for idx, row in df_hugging_face.iterrows():
        logger.warning(f"Processing row {idx+1}/{len(df_hugging_face)}")
        prompt = generate_prompt_for_test(row["question"], row["context"], SQL_MOTOR)
        response = send_prompt(prompt)
        sql_statement, explanation = get_sql_and_explanation(response)
        sql_generados.append(sql_statement)
        time.sleep(4)

except Exception as e:
        logger.error(f"Error processing row {idx+1}: {e}")
finally:
        logger.warning("Finished processing.")
        df_hugging_face = df_hugging_face.head(len(sql_generados))
        df_hugging_face["sql_generado"] = sql_generados

        df_hugging_face.to_csv(PATH_OUTPUT_FILE, index=False, sep="|")
        logger.warning("Results saved to resultado_in: " + PATH_OUTPUT_FILE)

logger.warning("----------------------------End test------------------------------------")
