import networkx as nx
import pandas as pd
import os
import sys
import json
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path
src_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(src_dir))

from config.config_yaml_loader import load_config


config = load_config()

class SQLResultValidator:
    def __init__(self, tolerance: float = 1e-6, strict_column_names: bool = False):
        """
        Inicializa el validador con tolerancia para comparaciones numéricas.
        
        Args:
            tolerance: Tolerancia para comparación de valores flotantes
            strict_column_names: Si True, los nombres de columnas deben ser exactos.
                                Si False, compara solo por posición y cantidad.
        """
        self.tolerance = tolerance
        self.strict_column_names = strict_column_names
    
    def normalize_result(self, result: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normaliza el resultado para hacer la comparación más robusta.
        Convierte valores None a null, ordena claves, etc.
        """
        normalized = []
        for row in result:
            normalized_row = {}
            for key, value in row.items():
                # Normalizar claves (quitar espacios, convertir a mayúsculas)
                normalized_key = key.strip().upper()
                
                # Normalizar valores numéricos
                if isinstance(value, (int, float)):
                    normalized_row[normalized_key] = float(value)
                else:
                    normalized_row[normalized_key] = value
                    
            normalized.append(normalized_row)
        
        # Ordenar las filas por las claves para hacer la comparación independiente del orden
        return sorted(normalized, key=lambda x: json.dumps(x, sort_keys=True))
    
    def exact_match(self, actual: List[Dict], predicted: List[Dict]) -> bool:
        """
        Verifica si los resultados son exactamente iguales.
        """
        actual_norm = self.normalize_result(actual)
        predicted_norm = self.normalize_result(predicted)
        
        return actual_norm == predicted_norm
    
    def structural_match(self, actual: List[Dict], predicted: List[Dict]) -> bool:
        """
        Verifica si la estructura es la misma.
        - Si strict_column_names=True: mismas columnas exactas y mismo número de filas
        - Si strict_column_names=False: mismo número de columnas y filas
        """
        if len(actual) != len(predicted):
            return False
        
        if not actual and not predicted:
            return True
        
        actual_col_count = len(actual[0].keys()) if actual else 0
        predicted_col_count = len(predicted[0].keys()) if predicted else 0
        
        if self.strict_column_names:
            # Comparación estricta: nombres exactos
            actual_keys = set(actual[0].keys()) if actual else set()
            predicted_keys = set(predicted[0].keys()) if predicted else set()
            return actual_keys == predicted_keys
        else:
            # Comparación flexible: solo cantidad de columnas
            return actual_col_count == predicted_col_count
    
    def value_accuracy(self, actual: List[Dict], predicted: List[Dict]) -> float:
        """
        Calcula el porcentaje de valores correctos considerando tolerancia numérica.
        - Si strict_column_names=True: compara por nombres exactos de columnas
        - Si strict_column_names=False: compara por posición de columnas
        """
        if not actual and not predicted:
            return 1.0
        
        if len(actual) != len(predicted):
            return 0.0
        
        total_values = 0
        correct_values = 0
        
        actual_norm = self.normalize_result(actual)
        predicted_norm = self.normalize_result(predicted)
        
        if self.strict_column_names:
            # Comparación estricta por nombres de columnas
            for act_row, pred_row in zip(actual_norm, predicted_norm):
                for key in act_row.keys():
                    if key in pred_row:
                        total_values += 1
                        if self._values_match(act_row[key], pred_row[key]):
                            correct_values += 1
        else:
            # Comparación flexible por posición
            for act_row, pred_row in zip(actual_norm, predicted_norm):
                act_values = list(act_row.values())
                pred_values = list(pred_row.values())
                
                # Solo comparar si tienen el mismo número de columnas
                if len(act_values) == len(pred_values):
                    for act_val, pred_val in zip(act_values, pred_values):
                        total_values += 1
                        if self._values_match(act_val, pred_val):
                            correct_values += 1
        
        return correct_values / total_values if total_values > 0 else 0.0
    
    def _values_match(self, actual_val, predicted_val) -> bool:
        """
        Verifica si dos valores coinciden considerando tolerancia numérica.
        """
        # Comparación numérica con tolerancia
        if isinstance(actual_val, (int, float)) and isinstance(predicted_val, (int, float)):
            return abs(actual_val - predicted_val) <= self.tolerance
        # Comparación exacta para otros tipos
        else:
            return actual_val == predicted_val
    
    def column_accuracy(self, actual: List[Dict], predicted: List[Dict]) -> float:
        """
        Calcula el porcentaje de columnas correctamente identificadas.
        - Si strict_column_names=True: nombres exactos de columnas
        - Si strict_column_names=False: solo cuenta de columnas (siempre 1.0 si coincide estructura)
        """
        if not actual and not predicted:
            return 1.0
        
        if self.strict_column_names:
            # Comparación estricta por nombres
            actual_columns = set()
            predicted_columns = set()
            
            for row in actual:
                actual_columns.update(row.keys())
            
            for row in predicted:
                predicted_columns.update(row.keys())
            
            if not actual_columns and not predicted_columns:
                return 1.0
            
            correct_columns = actual_columns.intersection(predicted_columns)
            total_columns = actual_columns.union(predicted_columns)
            
            return len(correct_columns) / len(total_columns) if total_columns else 0.0
        else:
            # Comparación flexible: solo verifica que tengan el mismo número de columnas
            if not actual or not predicted:
                return 0.0
            
            actual_col_count = len(actual[0].keys()) if actual else 0
            predicted_col_count = len(predicted[0].keys()) if predicted else 0
            
            return 1.0 if actual_col_count == predicted_col_count else 0.0
    
    def row_accuracy(self, actual: List[Dict], predicted: List[Dict]) -> float:
        """
        Calcula el porcentaje de filas completamente correctas.
        """
        if not actual and not predicted:
            return 1.0
        
        if len(actual) != len(predicted):
            # Penalizar si el número de filas es diferente
            return max(0, 1 - abs(len(actual) - len(predicted)) / max(len(actual), len(predicted)))
        
        actual_norm = self.normalize_result(actual)
        predicted_norm = self.normalize_result(predicted)
        
        correct_rows = 0
        
        
        # Comparación flexible por posición
        for act_row, pred_row in zip(actual_norm, predicted_norm):
            act_values = list(act_row.values())
            pred_values = list(pred_row.values())
            
            if len(act_values) == len(pred_values):
                row_correct = all(self._values_match(av, pv) for av, pv in zip(act_values, pred_values))
                if row_correct:
                    correct_rows += 1
        
        return correct_rows / len(actual) if actual else 0.0
    
    def get_comprehensive_metrics(self, actual: List[Dict], predicted: List[Dict]) -> Dict[str, float]:
        """
        Calcula todas las métricas de una vez.
        """
        return {
            'exact_match': float(self.exact_match(actual, predicted)),
            'structural_match': float(self.structural_match(actual, predicted)),
            'value_accuracy': self.value_accuracy(actual, predicted),
            'column_accuracy': self.column_accuracy(actual, predicted),
            'row_accuracy': self.row_accuracy(actual, predicted),
            'overall_score': self._calculate_overall_score(actual, predicted)
        }
    
    def _calculate_overall_score(self, actual: List[Dict], predicted: List[Dict]) -> float:
        """
        Calcula un score general ponderado.
        """
        exact = self.exact_match(actual, predicted)
        if exact:
            return 1.0
        
        # Ponderación de diferentes métricas
        weights = {
            'structural': 0.3,
            'value': 0.4,
            'column': 0.2,
            'row': 0.1
        }
        
        scores = {
            'structural': float(self.structural_match(actual, predicted)),
            'value': self.value_accuracy(actual, predicted),
            'column': self.column_accuracy(actual, predicted),
            'row': self.row_accuracy(actual, predicted)
        }
        
        weighted_score = sum(score * weights[metric] for metric, score in scores.items())
        return weighted_score


def validate_sql_results(df: pd.DataFrame, strict_column_names: bool = False) -> pd.DataFrame:
    """
    Valida resultados SQL en un DataFrame de pandas.
    
    Args:
        df: DataFrame con columnas 'resultado_sql' y 'resultado_sql_generado_llm'
        strict_column_names: Si True, los nombres de columnas deben coincidir exactamente.
                           Si False, compara solo por posición y valores (recomendado para SQL con alias)
    
    Returns:
        DataFrame con métricas añadidas
    """
    validator = SQLResultValidator(strict_column_names=strict_column_names)
    
    # Calcular métricas para cada fila
    metrics_list = []
    for _, row in df.iterrows():
        actual = row['resultado_sql']
        predicted = row['resultado_sql_generado_llm']
        
        # Función auxiliar para parsear el valor
        def parse_value(value):
            if isinstance(value, list):
                return value
            if isinstance(value, str):
                # Verificar si es un error SQL
                sql_error_indicators = [
                    'Error',
                    'OperationalError',
                    'no such table',
                    'no such column',
                    'syntax error',
                    'near "',
                    'SQL:',
                    'sqlite3.',
                    'pymysql.',
                    'psycopg2.',
                    'Exception',
                    'Traceback'
                ]
                
                # Si contiene indicadores de error SQL, retornar lista vacía
                if any(indicator in value for indicator in sql_error_indicators):
                    return []
                
                # Intentar evaluar como Python literal
                try:
                    import ast
                    return ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    # Si falla, intentar como JSON
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        # Si todo falla, intentar reemplazar comillas simples
                        try:
                            return json.loads(value.replace("'", '"'))
                        except:
                            # Si no se puede parsear y no es un error SQL conocido, 
                            # asumir que es un error y retornar lista vacía
                            return []
            return value
        
        # Parsear los valores
        try:
            actual = parse_value(actual)
            predicted = parse_value(predicted)
            
            # Verificar si alguno de los valores es una lista vacía (indica error SQL)
            sql_error = False
            error_type = None
            
            if not actual and not predicted:
                # Ambos tienen errores
                sql_error = True
                error_type = "both_sql_errors"
            elif not actual:
                # Solo el resultado actual tiene error
                sql_error = True
                error_type = "actual_sql_error"
            elif not predicted:
                # Solo el resultado predicho tiene error
                sql_error = True
                error_type = "predicted_sql_error"
            
            if sql_error:
                metrics_list.append({
                    'exact_match': 0.0,
                    'structural_match': 0.0,
                    'value_accuracy': 0.0,
                    'column_accuracy': 0.0,
                    'row_accuracy': 0.0,
                    'overall_score': 0.0,
                    'error_type': error_type,
                    'has_sql_error': True
                })
                continue
                
        except Exception as e:
            print(f"Error parseando fila: {e}")
            # Añadir métricas de error
            metrics_list.append({
                'exact_match': 0.0,
                'structural_match': 0.0,
                'value_accuracy': 0.0,
                'column_accuracy': 0.0,
                'row_accuracy': 0.0,
                'overall_score': 0.0,
                'error_type': 'parsing_error',
                'has_sql_error': True,
                'error_message': str(e)
            })
            continue
        
        metrics = validator.get_comprehensive_metrics(actual, predicted)
        metrics_list.append(metrics)
    
    # Añadir métricas al DataFrame
    metrics_df = pd.DataFrame(metrics_list)
    result_df = pd.concat([df, metrics_df], axis=1)
    
    return result_df


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

VERSION = f"{PROMPT_METHOD}_{TIPO_PROMPT}".replace(".","_")
BASE_PATH = os.path.join("data", "analytics", "Nutresa", MODELO).replace(".","_")
PATH_INPUT_FILE = (os.path.join(BASE_PATH, f"out_{VERSION}")).replace(".","_") +".csv"
PATH_OUTPUT_FILE = (os.path.join(BASE_PATH, f"out_{MODELO}_metricas")).replace(".","_") +".xlsx"

print(f"Input file: {PATH_INPUT_FILE}")
print(f"Output file: {PATH_OUTPUT_FILE}")
df = pd.read_csv(PATH_INPUT_FILE, sep="|", encoding="latin-1")


# Agregamos la métrica de ETM
df['metrica_etm'] = df.apply(lambda row: evaluate_sql(str(row['sql_generado_llm']), str(row['SQL'])), axis=1)

#Si sql_generado es NaN, entonces la métrica de ETM es 0
df['metrica_etm'] = df.apply(lambda row: 0 if pd.isna(row['sql_generado_llm']) else row['metrica_etm'], axis=1)

print(df[(df['sql_generado_llm'].isna()) | (df['sql_generado_llm'] == '')].head())

df = df.fillna("Pregunta no relacionada")

df = validate_sql_results(df, True)

print(PATH_OUTPUT_FILE)
mode = "a" if os.path.exists(PATH_OUTPUT_FILE) else "w"

with pd.ExcelWriter(PATH_OUTPUT_FILE, engine="openpyxl", mode=mode) as writer: #, if_sheet_exists='replace'
    df.to_excel(writer, index=False, sheet_name=VERSION)
