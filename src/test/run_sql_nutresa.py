import pandas as pd
import sys
import warnings
import pandasql as ps
from pathlib import Path
src_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(src_dir))

from utils.data import read_data_and_definition
from config.config_yaml_loader import load_config
import logging
from logs.config_logging import setup_logging



warnings.filterwarnings("ignore", category=FutureWarning)


# Setup the logs
setup_logging()
logger = logging.getLogger(__name__)

# Load configuration settings from a YAML file.
config = load_config()
PATH_RAW_DATA = config.get("paths", {}).get("raw_data")
PATH_RAW_DATA_DEFINITION = config.get("paths", {}).get("raw_data_definition")


test_data = pd.read_excel("data/raw/Consultas Nutresa.xlsx")

def ejecutar_sql_pandasql(row):
    """Ejecuta la sentencia SQL de una fila usando pandasql y registra el resultado o el error."""
    try:
        sentencia_sql = row['SQL']
        env = {"df": df}
        resultado = ps.sqldf(sentencia_sql, env)
        return resultado.to_dict('records')
    except Exception as e:
        return str(e).replace("\t", " ")


df, str_full_context = read_data_and_definition(PATH_RAW_DATA, PATH_RAW_DATA_DEFINITION)



test_data['resultado_sql'] = test_data.apply(ejecutar_sql_pandasql, axis=1)

# Guardar el DataFrame con la nueva columna en un nuevo archivo CSV o sobrescribir el existente
nombre_archivo_salida = 'data/stage/consultas_nutresa_resueltas_v2_test.csv'
test_data.to_csv(nombre_archivo_salida, index=False, sep="\t", encoding="latin-1")
