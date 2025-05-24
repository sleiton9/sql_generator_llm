import networkx as nx
import pandas as pd
import os
from config.config_yaml_loader import load_config

config = load_config()

def build_tree(sql_query):
    """Convierte una consulta SQL en un grafo dirigido (árbol)."""
    tree = nx.DiGraph()
    # Simulación de parsing SQL (en producción usar sqlparse o ANTLR)
    tokens = sql_query.replace(',', '').split()
    parent = "ROOT"
    tree.add_node(parent)
    for token in tokens:
        tree.add_node(token)
        tree.add_edge(parent, token)
        parent = token if token.upper() in {"SELECT", "FROM", "WHERE"} else parent
    return tree

def tree_similarity(tree1, tree2):
    """Calcula la similitud entre dos árboles usando coincidencia de nodos."""
    nodes1, nodes2 = set(tree1.nodes), set(tree2.nodes)
    common_nodes = nodes1 & nodes2
    similarity = 2 * len(common_nodes) / (len(nodes1) + len(nodes2))
    return similarity

def evaluate_sql(predicted_sql, reference_sql):
    """Evalúa la consulta generada en comparación con la referencia usando ETM."""
    tree_pred = build_tree(predicted_sql)
    tree_ref = build_tree(reference_sql)
    structural_similarity = tree_similarity(tree_pred, tree_ref)
    return structural_similarity


LLM_MODEL = config.get("llm_model", "gemini").lower().strip()
if LLM_MODEL == "gemini":
      MODELO = config.get("gemini_model").lower().strip()
elif LLM_MODEL == "chatgpt":
      MODELO = config.get("chatgpt_model").lower().strip()
TEMPERATURA = config.get("temperature")
TOP_P = config.get("top_p")
TIPO_PROMPT = config.get("tipo_prompt")
PROMPT_METHOD = config.get("prompt_method", "zero_shot").lower().strip()


VERSION = f"{PROMPT_METHOD}_{TIPO_PROMPT}_t{TEMPERATURA}_top{TOP_P}".replace(".","_")


# Definir la ruta base
base_path = os.path.join("data", "analytics", "Hugging_Face", MODELO).replace(".", "_")

# Crear las rutas de archivos usando os.path.join()
INPUT_FILE = os.path.join(base_path, f"out_{MODELO}_{VERSION}".replace(".", "_") + ".csv")
OUTPUT_FILE = os.path.join(base_path, f"metricas_{MODELO}".replace(".", "_") + ".xlsx")


print(f"Input file: {INPUT_FILE}")
df = pd.read_csv(INPUT_FILE, sep="|")


# Agregamos la métrica de ETM
df['metrica_etm'] = df.apply(lambda row: evaluate_sql(str(row['sql_generado']), str(row['answer'])), axis=1)

#Si sql_generado es NaN, entonces la métrica de ETM es 0
df['metrica_etm'] = df.apply(lambda row: 0 if pd.isna(row['sql_generado']) else row['metrica_etm'], axis=1)

print(df[(df['sql_generado'].isna()) | (df['sql_generado'] == '')].head())

df = df.fillna("Pregunta no relacionada")


print(OUTPUT_FILE)
mode = "a" if os.path.exists(OUTPUT_FILE) else "w"

with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl", mode=mode) as writer:
    df.to_excel(writer, index=False, sheet_name=VERSION)
