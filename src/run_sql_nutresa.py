import pandas as pd
from utils.data import read_data_and_definition, query_data
from config.config_yaml_loader import load_config
import logging
from logs.config_logging import setup_logging
import warnings
import pandasql as ps


warnings.filterwarnings("ignore", category=FutureWarning)


# Setup the logs
setup_logging()
logger = logging.getLogger(__name__)

# Load configuration settings from a YAML file.
config = load_config()
PATH_RAW_DATA = config.get("paths", {}).get("raw_data")
PATH_RAW_DATA_DEFINITION = config.get("paths", {}).get("raw_data_definition")


test_data = pd.read_excel("data/raw/Consultas_Nutresa_V2.xlsx")
# test_data = pd.read_excel("data/raw/Preguntas_Nutresa_Revisadas.xlsx", sheet_name="Preguntas")

def ejecutar_sql_pandasql(row):
    """Ejecuta la sentencia SQL de una fila usando pandasql y registra el resultado o el error."""
    try:
        sentencia_sql = row['SQL']  # Reemplaza 'sql_query' con el nombre de tu columna SQL
        # Definir un entorno global para que pandasql acceda al DataFrame 'df'
        env = {"df": df}
        resultado = ps.sqldf(sentencia_sql, env)
        return resultado.to_dict('records')  # Convertir el DataFrame resultante a una lista de diccionarios
    except Exception as e:
        return str(e).replace("\t", " ")  # Devolver el error como cadena


df, str_full_context = read_data_and_definition(PATH_RAW_DATA, PATH_RAW_DATA_DEFINITION)

# print(test_data.head())

# test_data.to_csv("data/raw/Preguntas_Nutresa_Revisadas_mal.csv", index=False, sep="|")

# pregunta = test_data.iloc[0][0]
# print(pregunta)
# query = test_data.iloc[0][2]
# print(query)

# df_result = query_data(df, query)
# print(df_result)

print(test_data.head())

test_data['resultado_sql'] = test_data.apply(ejecutar_sql_pandasql, axis=1)

# Guardar el DataFrame con la nueva columna en un nuevo archivo CSV o sobrescribir el existente
nombre_archivo_salida = 'data/stage/consultas_nutresa_resueltas_v2.csv'  # Reemplaza con el nombre deseado
test_data.to_csv(nombre_archivo_salida, index=False, sep="\t", encoding="latin-1")
