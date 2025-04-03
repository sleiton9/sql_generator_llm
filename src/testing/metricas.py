import networkx as nx
import pandas as pd
from sqlfluff.core import Linter

def is_sql_syntax_correct(sql_query: str, dialect: str = "ansi") -> bool:
    """
    Verifica la sintaxis de una consulta SQL utilizando sqlfluff.
    
    Args:
        sql_query (str): La consulta SQL a validar.
        dialect (str): El dialecto SQL a utilizar (por defecto "ansi").
        
    Returns:
        bool: True si la consulta es sintácticamente correcta, False en caso contrario.
    """ 
    linter = Linter(dialect=dialect, exclude_rules=['LT05', 'LT14', 'LT12', 'LT09'])
    lint_result = linter.lint_string(sql_query)
    # Si existen errores o advertencias, check_tuples() retornará una lista no vacía
    return not lint_result.check_tuples()

def get_failed_rules(sql_query: str, dialect: str = "ansi") -> list:
    """
    Obtiene una lista de las reglas que fallaron al validar la consulta SQL.
    
    Args:
        sql_query (str): La consulta SQL a validar.
        dialect (str): El dialecto SQL a utilizar (por defecto "ansi").
    
    Returns:
        list: Lista de códigos de reglas que fallaron.
    """
    linter = Linter(dialect=dialect, exclude_rules=['LT05', 'LT14', 'LT12', 'LT09'])
    lint_result = linter.lint_string(sql_query)
    # Extraer los códigos de las reglas que fallaron
    failed_rules = [violation.rule_code for violation in lint_result.violations]
    # Opcional: eliminar duplicados si fuese necesario
    return list(set(failed_rules))

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

# # Ejemplo de consulta SQL
# sql = 'SELECT name, born_state, age FROM head ORDER BY age'

# # Prueba de verificación de sintaxis y obtención de reglas falladas
# syntax_correct = is_sql_syntax_correct(sql)
# failed = get_failed_rules(sql)
# print(f"SQL correcto: {syntax_correct}")
# print(f"Reglas falladas: {failed}")


MODELO = "gemini-20-flash" 
INPUT_FILE = f"src/testing/{MODELO}/sql_generados_gemini_20.csv" #src/testing/gemini-20-flash-lite/resultado_con_sql_generado_389.csv  src/testing/gpt-35-turbo/sql_generados_chat_35.csv
OUTPUT_FILE = f"src/testing/{MODELO}/metricas_gemini2.csv"

df = pd.read_csv(INPUT_FILE, sep="|")
# df.to_csv(OUTPUT_FILE, index=False, sep="\t")



print(df.dtypes)
# Agregamos la métrica de ETM y la verificación sintáctica, además de la columna con las reglas falladas
df['metrica_etm'] = df.apply(lambda row: evaluate_sql(str(row['sql_generado']), str(row['answer'])), axis=1)
# df['exactitud_sintactica'] = df['sql_generado'].apply(is_sql_syntax_correct)
# df['failed_rules'] = df['sql_generado'].apply(get_failed_rules)
print(df.head())


df.to_csv(OUTPUT_FILE, index=False, sep="|", decimal=",")
