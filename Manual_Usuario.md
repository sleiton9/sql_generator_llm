# Manual de Usuario - Generador de SQL con Modelos de Lenguaje Natural

## Tabla de Contenidos
1. [Introducción](#introducción)
2. [Configuración Inicial](#configuración-inicial)
3. [Configuración de API Keys](#configuración-de-api-keys)
4. [Configuración de Métodos de Prompt](#configuración-de-métodos-de-prompt)
5. [Personalización de Reglas de Negocio](#personalización-de-reglas-de-negocio)
6. [Configuración de Modelos LLM](#configuración-de-modelos-llm)
7. [Configuración del Motor SQL](#configuración-del-motor-sql)
8. [Configuración de Hiperparámetros](#configuración-de-hiperparámetros)
9. [Personalización de Prompts](#personalización-de-prompts)
10. [Preparación de Datos](#preparación-de-datos)
11. [Uso de la Aplicación](#uso-de-la-aplicación)
12. [Ejemplos Prácticos](#ejemplos-prácticos)
13. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

Este sistema permite convertir preguntas en lenguaje natural a consultas SQL utilizando modelos de lenguaje de gran escala (LLM). La aplicación soporta múltiples estrategias de generación de prompts y es compatible con diferentes modelos como Gemini y ChatGPT.

**Limitación importante**: La aplicación actualmente **solo funciona con archivos CSV** como base de datos, utilizando `pandasql` como motor SQL para ejecutar consultas sobre DataFrames de pandas.

---

## Configuración Inicial

### Paso 1: Crear el archivo de configuración

1. Navega a la carpeta `src/config/`
2. Copia el archivo `config_example.yaml`
3. Renómbralo como `config.yaml`

```bash
cp src/config/config_example.yaml src/config/config.yaml
```

### Paso 2: Estructura del archivo de configuración

El archivo `config.yaml` contiene todas las configuraciones necesarias para el funcionamiento del sistema:

```yaml
# Configuración general
llm_model: gemini # gemini, chatgpt
prompt_method: few_shot # zero_shot, few_shot, rag

# Configuración para zero_shot y few_shot
sql_motor: ansi #pandasql, ansi
table_name: df

# Configuración Gemini
gemini_api_key: TU_API_KEY_AQUI
gemini_model: gemini-2.0-flash
gemini_embedding_model: gemini-embedding-exp-03-07
threshold_similarity_rag: 0.59

# Configuración ChatGPT
chatgpt_api_key: TU_API_KEY_AQUI
chatgpt_model: gpt-3.5-turbo

# Hiperparámetros (valores por defecto recomendados)
temperature: 0.1
max_output_tokens: 512
top_p: 0.2
```

---

## Configuración de API Keys

### Para usar Gemini:
1. Visita [Google AI Studio](https://aistudio.google.com/)
2. Genera tu API key
3. En el archivo `config.yaml`, reemplaza:
```yaml
gemini_api_key: TU_API_KEY_DE_GEMINI_AQUI
```

### Para usar ChatGPT:
1. Visita [OpenAI Platform](https://platform.openai.com/)
2. Genera tu API key
3. En el archivo `config.yaml`, reemplaza:
```yaml
chatgpt_api_key: TU_API_KEY_DE_OPENAI_AQUI
```

---

## Configuración de Métodos de Prompt

El sistema soporta tres métodos de generación de prompts:

### 1. Zero-Shot
No utiliza ejemplos, solo el contexto de la base de datos.
```yaml
prompt_method: zero_shot
```

### 2. Few-Shot (Recomendado)
Utiliza ejemplos predefinidos para mejorar la precisión.
```yaml
prompt_method: few_shot
```

### 3. RAG (Retrieval-Augmented Generation)
Utiliza un sistema de recuperación basado en embeddings.
```yaml
prompt_method: rag
```

---

## Configuración del Método RAG (Opcional)

Si deseas utilizar el método RAG (Retrieval-Augmented Generation), necesitas configurar un archivo JSON adicional que contenga el contexto estructurado de tu base de datos para generar embeddings.

### Ubicación del Archivo RAG

El archivo debe ubicarse en: `data/stage/rag_db_context.json`

### Configuración Adicional en config.yaml

Para RAG, asegúrate de tener configurados estos parámetros:

```yaml
# Método RAG
prompt_method: rag

# Configuración específica para RAG
gemini_embedding_model: gemini-embedding-exp-03-07
threshold_similarity_rag: 0.59  # Umbral de similitud (0.0-1.0)
```

### Estructura del Archivo rag_db_context.json

El archivo JSON debe seguir esta estructura exacta:

```json
{
  "Bases_de_datos": [
    {
      "Nombre_base_de_datos": "nombre_de_tu_base_de_datos",
      "Tipo_base_de_datos": "CSV/Pandas",
      "Tablas": [
        {
          "Nombre_tabla": "df",
          "Columnas": [
            {
              "Nombre_del_campo": "NOMBRE_COLUMNA_1",
              "Tipo_campo": "VARCHAR/INTEGER/DECIMAL/DATE",
              "Definicion": "Descripción detallada del campo y su propósito",
              "Ejemplos": "Ejemplo1, Ejemplo2, Ejemplo3",
              "Relaciones": "Relación con otros campos si aplica",
              "Restricciones": "Restricciones o reglas de negocio específicas"
            },
            {
              "Nombre_del_campo": "NOMBRE_COLUMNA_2",
              "Tipo_campo": "INTEGER",
              "Definicion": "Descripción del segundo campo",
              "Ejemplos": "100, 250, 500",
              "Relaciones": "None",
              "Restricciones": "Valores positivos únicamente"
            }
          ]
        }
      ]
    }
  ]
}
```

### Consideraciones Importantes para RAG

#### 1. Calidad de las Descripciones
- **Definiciones claras**: Cada campo debe tener una descripción detallada y precisa
- **Ejemplos representativos**: Incluye ejemplos reales que ayuden a entender el contenido
- **Contexto de negocio**: Agrega información sobre cómo se usa el campo en tu organización

#### 2. Configuración del Umbral de Similitud
```yaml
threshold_similarity_rag: 0.59  # Ajusta según tus necesidades
```

- **Valores altos (0.7-0.9)**: Más restrictivo, solo contexto muy relevante
- **Valores medios (0.5-0.7)**: Balance entre precisión y cobertura
- **Valores bajos (0.3-0.5)**: Más permisivo, incluye más contexto

#### 3. Ventajas del Método RAG

- **Contexto dinámico**: Solo incluye información relevante para cada pregunta
- **Mejor para bases de datos grandes**: Maneja eficientemente muchas columnas
- **Precisión mejorada**: Reduce la confusión al limitar el contexto
- **Escalabilidad**: Funciona mejor con esquemas complejos

#### 4. Cuándo Usar RAG

- Bases de datos con más de 50 columnas
- Múltiples tablas o esquemas complejos
- Cuando el contexto completo excede los límites del modelo
- Necesidad de mayor precisión en consultas específicas

### Proceso de Generación de Embeddings

Cuando usas RAG, el sistema:

1. **Lee el archivo JSON** con la estructura de tu base de datos
2. **Genera embeddings** para cada columna usando el modelo de Gemini
3. **Construye un vector store** en memoria
4. **Para cada pregunta**:
   - Genera embedding de la pregunta
   - Busca columnas similares usando similitud coseno
   - Incluye solo el contexto relevante en el prompt

### Ejemplo de Uso con RAG

```bash
# Ejecutar con método RAG configurado
python src/__main__.py
```

```
¿Cuál es tu duda frente a los datos?
> ¿Cuáles son los productos más vendidos en la región Norte?

# El sistema automáticamente:
# 1. Genera embedding para la pregunta
# 2. Encuentra columnas relevantes: PRODUCTO, CANTIDAD, REGION
# 3. Incluye solo ese contexto en el prompt
# 4. Genera la consulta SQL optimizada
```

### Verificación de la Configuración RAG

Para probar tu configuración RAG, puedes ejecutar:

```bash
python src/test/test_rag.py
```

Este script te mostrará:
- Si el archivo JSON se lee correctamente
- Cuántos embeddings se generaron
- Resultados de una consulta de prueba
- Scores de similitud

### Solución de Problemas RAG

**Problema**: "No se encuentran resultados relevantes"
- **Solución**: Reduce el `threshold_similarity_rag`
- Mejora las descripciones en el JSON

**Problema**: "Embeddings no se generan"
- **Solución**: Verifica tu API key de Gemini
- Confirma que el archivo JSON tenga la estructura correcta

**Problema**: "Respuestas imprecisas"
- **Solución**: Aumenta el `threshold_similarity_rag`
- Mejora la calidad de las definiciones y ejemplos

---

## Personalización de Reglas de Negocio

### Modificando Ejemplos en Few-Shot

Para agregar reglas de negocio específicas, modifica la sección `prompt_few_shot` en el archivo `config.yaml`:

```yaml
prompt_few_shot: |
    {instrucciones}

    ### CONTEXTO ###
    # El motor SQL será: {sql_motor}
    # El nombre de la tabla es: {table_name}
    # Este es el contexto de la tabla en la cual se debe basar la consulta: 
    # {context}

    ## EJEMPLOS ###
    # Para esta pregunta ¿Cuál fue la cantidad total vendida por sector del producto en 2024 en la ciudad Bogota? El resultado esperado es: SELECT DES_SECTOR, SUM(VENTA_VOLUMEN) FROM df WHERE ANIO= 2024 AND DES_CIUDAD= 'Bogota' GROUP BY DES_SECTOR;
    # Para esta pregunta ¿Cuántas ventas se realizaron en el año 2023? El resultado esperado es: SELECT COUNT(*) FROM df WHERE ANIO= 2023;
    # Para esta pregunta ¿Cuál es el precio promedio de venta por línea y tipo de fabricante en el ultimo año? El resultado esperado es: SELECT DES_LINEA, DES_TIPO_FABRICANTE, AVG(VENTA_PRECIO) FROM df WHERE ANIO= 2024 GROUP BY DES_LINEA, DES_TIPO_FABRICANTE;
    
    # AGREGA TUS EJEMPLOS ESPECÍFICOS AQUÍ:
    # Para esta pregunta ¿Cuál es el cliente con mayor facturación en el trimestre actual? El resultado esperado es: SELECT CLIENTE, SUM(FACTURACION) as TOTAL_FACTURACION FROM df WHERE TRIMESTRE = 'Q1' GROUP BY CLIENTE ORDER BY TOTAL_FACTURACION DESC LIMIT 1;
    # Para esta pregunta ¿Qué productos tienen margen de ganancia superior al 20%? El resultado esperado es: SELECT PRODUCTO, MARGEN FROM df WHERE MARGEN > 0.20;

    ## RESPUESTA ###
    # Por favor, razona paso a paso cómo traducir la pregunta a SQL. Sin embargo, devuelve EXCLUSIVAMENTE el JSON en un bloque de código delimitado por triple backticks ``` con las dos llaves indicadas.
    # Generar un solo SQL a la vez, no generar varios SQLs. Si se requiere generar varios SQLs dejar null la llave de sql_statement y generar la explicacion de que no se puede generar varias consultas al tiempo.
    # Para este primer prompt solo responder con una confirmacion de que entendiste las instrucciones y el contexto, sin hacer nada más.
```

### Reglas de Negocio Específicas que Puedes Agregar:

#### 1. Reglas de Fechas
```yaml
# Para preguntas sobre "mes actual" usar: WHERE EXTRACT(MONTH FROM fecha) = EXTRACT(MONTH FROM CURRENT_DATE)
# Para "año pasado": WHERE ANIO = EXTRACT(YEAR FROM CURRENT_DATE) - 1
```

#### 2. Reglas de Rangos
```yaml
# Para "productos caros": WHERE PRECIO > (SELECT AVG(PRECIO) * 1.5 FROM df)
# Para "clientes VIP": WHERE TOTAL_COMPRAS > 1000000
```

#### 3. Reglas de Agrupación
```yaml
# Siempre agrupar ventas por región cuando se mencione "por región"
# Usar HAVING para filtros después de GROUP BY
```

#### 4. Reglas de Formato
```yaml
# Para montos: FORMAT(SUM(monto), 2) 
# Para porcentajes: ROUND((campo/total)*100, 2)
```

### Ejemplo Completo de Personalización:

```yaml
## EJEMPLOS ###
# REGLAS DE NEGOCIO ESPECÍFICAS:
# - Cuando se pregunte por "productos rentables", usar margen > 15%
# - "Clientes importantes" son aquellos con facturación > 500000
# - "Período actual" se refiere al año 2024
# - Siempre ordenar resultados de mayor a menor cuando se pida "top" o "mayor"

# Para esta pregunta ¿Cuáles son los productos más rentables? El resultado esperado es: SELECT PRODUCTO, MARGEN FROM df WHERE MARGEN > 0.15 ORDER BY MARGEN DESC;
# Para esta pregunta ¿Quiénes son nuestros clientes importantes en el período actual? El resultado esperado es: SELECT CLIENTE, SUM(FACTURACION) as TOTAL FROM df WHERE ANIO = 2024 GROUP BY CLIENTE HAVING SUM(FACTURACION) > 500000 ORDER BY TOTAL DESC;
# Para esta pregunta ¿Cuál es el top 5 de vendedores por comisiones? El resultado esperado es: SELECT VENDEDOR, SUM(COMISION) as TOTAL_COMISION FROM df GROUP BY VENDEDOR ORDER BY TOTAL_COMISION DESC LIMIT 5;
```

### Configuración para Empresa de Servicios:

```yaml
## EJEMPLOS ###
# REGLAS DE NEGOCIO - SERVICIOS:
# - "Clientes activos": con transacciones en los últimos 3 meses
# - "Servicios rentables": margen superior al 30%
# - "Peak hours": entre 9:00 y 17:00
# - "Retención alta": clientes con más de 2 años de antigüedad

# Para esta pregunta ¿Cuántos clientes activos tenemos? El resultado esperado es: SELECT COUNT(DISTINCT CLIENTE) as CLIENTES_ACTIVOS FROM df WHERE FECHA >= DATE_SUB(CURRENT_DATE, INTERVAL 3 MONTH);

# Para esta pregunta ¿Cuáles servicios son más rentables? El resultado esperado es: SELECT SERVICIO, AVG(MARGEN) as MARGEN_PROMEDIO FROM df GROUP BY SERVICIO HAVING AVG(MARGEN) > 0.30 ORDER BY MARGEN_PROMEDIO DESC;
```

---

## Configuración de Modelos LLM

### Cambiar el Modelo Principal:

```yaml
# Para usar Gemini
llm_model: gemini
gemini_model: gemini-2.0-flash  # o gemini-2.0-flash-lite

# Para usar ChatGPT
llm_model: chatgpt
chatgpt_model: gpt-3.5-turbo  # o gpt-4
```

### Modelos Disponibles:

**Gemini:**
- `gemini-2.0-flash` (Recomendado)
- `gemini-2.0-flash-lite`

**ChatGPT:**
- `gpt-3.5-turbo`
- `gpt-4`

---

## Configuración del Motor SQL

**Importante**: La aplicación actualmente solo soporta motores SQL compatibles con pandas:

```yaml
sql_motor: ansi  # Recomendado
# sql_motor: pandasql  # Alternativo
```

### Limitaciones del Motor SQL:
- Solo funciona con archivos CSV
- Utiliza `pandasql` internamente
- La tabla siempre se llama `df`
- No soporta bases de datos relacionales directas

```yaml
table_name: df  # No cambiar este valor
```

---

## Configuración de Hiperparámetros

Los valores por defecto están optimizados, pero puedes ajustarlos según tus necesidades:

```yaml
# Valores recomendados (mejores resultados en pruebas)
temperature: 0.1      # Creatividad (0.0-1.0, menor = más determinista)
max_output_tokens: 512  # Longitud máxima de respuesta
top_p: 0.2           # Diversidad de tokens (0.0-1.0)
```

### Guía de Ajuste:

- **Temperature**: 
  - 0.0-0.2: Respuestas más consistentes y deterministas
  - 0.3-0.7: Balance entre creatividad y consistencia
  - 0.8-1.0: Más creatividad, menos predecible

- **Top_p**:
  - 0.1-0.3: Respuestas más enfocadas
  - 0.4-0.7: Balance
  - 0.8-1.0: Mayor diversidad

---

## Personalización de Prompts

### Estructura de Prompts:

```yaml
prompt_general_instructions: |
    ### INSTRUCCIONES ###
    # Este es un prompt donde se definen las instrucciones a seguir, despues de este se enviaran las preguntas del usuario.
    # El usuario te hará una pregunta en lenguaje natural y tu salida debe ser EXCLUSIVAMENTE un objeto JSON con dos claves:
    #    1) "sql_statement": que contenga la sentencia SQL optimizada necesaria (sin explicaciones internas).
    #    2) "explanation": que describa en lenguaje natural cómo interpretar o usar el resultado, agregando las columnas de la fuente y las agregaciones usadas de la consulta (sin mencionar directamente que se genera un SQL internamente para generar el resultado).
    #        Si la pregunta NO está relacionada con la tabla o los datos, entonces:
    #            - "sql_statement": null
    #            - "explanation": "La pregunta no está relacionada con los datos."
```

### Personalizando Instrucciones:

Puedes modificar las instrucciones para agregar reglas específicas:

```yaml
prompt_general_instructions: |
    ### INSTRUCCIONES ###
    # REGLAS ESPECÍFICAS DE TU ORGANIZACIÓN:
    # - Siempre usar mayúsculas para nombres de columnas
    # - Incluir validaciones de datos nulos
    # - Formatear números con 2 decimales
    # - Usar alias descriptivos para columnas calculadas
    
    # El usuario te hará una pregunta en lenguaje natural y tu salida debe ser EXCLUSIVAMENTE un objeto JSON con dos claves:
    #    1) "sql_statement": que contenga la sentencia SQL optimizada necesaria (sin explicaciones internas).
    #    2) "explanation": que describa en lenguaje natural cómo interpretar o usar el resultado.
```

---

## Preparación de Datos

### Estructura de Archivos Requerida:

```
data/
├── raw/
│   ├── tu_archivo_de_datos.csv
│   └── definicion_de_campos.csv
```

### Formato del Archivo de Datos:
- **Formato**: CSV
- **Separador**: Punto y coma (;)
- **Codificación**: Latin-1
- **Encabezados**: Primera fila

### Formato del Archivo de Definiciones:
Debe contener al menos estas columnas:
- Nombre del campo
- Tipo de dato
- Descripción
- Ejemplos

### Configurar Rutas en config.yaml:

Modifica las rutas en `src/config/config_yaml_loader.py`:

```python
config["paths"] = {
    "project_root": project_root,
    "raw_data": os.path.join(
        project_root, "data", "raw", "TU_ARCHIVO_DE_DATOS.csv"
    ),
    "raw_data_definition": os.path.join(
        project_root, "data", "raw", "TU_ARCHIVO_DE_DEFINICIONES.csv"
    ),
    # ...
}
```

---

## Uso de la Aplicación

### Ejecutar la Aplicación:

```bash
python src/__main__.py
```

### Interfaz de Usuario:

1. La aplicación mostrará: `"Puedes realizar varias preguntas relacionada a los datos, Escribir 'exit' para salir."`
2. Ingresa tu pregunta en español
3. El sistema generará y ejecutará la consulta SQL
4. Mostrará el resultado y la explicación
5. Escribe `exit` para salir

### Ejemplo de Interacción:

```
¿Cuál es tu duda frente a los datos?
> ¿Cuál es el cliente que más vendió en agosto de 2024?

Explicación: Esta consulta muestra el cliente con mayor volumen de ventas en agosto de 2024, 
incluyendo el código del cliente y el total de ventas realizadas.

Resultado de la pregunta:
   CODIGO_CLIENTE  TOTAL_VENTAS
0           12345        1500000
```

---

## Solución de Problemas

### Problema: "API Key inválida"
**Solución**: Verifica que tu API key esté correctamente configurada en `config.yaml`

### Problema: "Error al leer datos"
**Solución**: 
- Verifica que el archivo CSV exista en la ruta especificada
- Confirma que el separador sea punto y coma (;)
- Verifica la codificación (Latin-1)

### Problema: "Consulta SQL incorrecta"
**Solución**:
- Revisa y mejora los ejemplos en la sección few-shot
- Ajusta la temperatura a un valor más bajo (0.1)
- Agrega más contexto en las definiciones de campos

### Problema: "Respuesta vacía o null"
**Solución**:
- La pregunta podría no estar relacionada con los datos
- Verifica que el contexto de la tabla sea completo
- Reformula la pregunta de manera más específica

### Problema: "Rate limit exceeded"
**Solución**:
- Espera unos minutos antes de hacer más consultas
- Para pruebas masivas, aumenta el tiempo de espera en el código

### Logs para Debugging:

Los logs se guardan en `src/logs/app.log` y contienen información detallada sobre:
- Prompts enviados
- Respuestas recibidas
- Errores de ejecución
- Uso de tokens

---

## Mejores Prácticas

1. **Siempre define reglas de negocio claras** en los ejemplos few-shot
2. **Usa nombres de campos descriptivos** en tu CSV
3. **Mantén el archivo de definiciones actualizado**
4. **Prueba con preguntas simples** antes de preguntas complejas
5. **Revisa los logs** para entender el comportamiento del sistema
6. **Ajusta los hiperparámetros** según tus necesidades específicas
7. **Mantén los ejemplos relevantes** a tu dominio de negocio

---

## Limitaciones Actuales

- Solo funciona con archivos CSV
- No soporta múltiples tablas o JOINs entre archivos
- El motor SQL está limitado a las capacidades de pandasql
- No hay interfaz web (solo línea de comandos)

---

## Próximas Versiones

- Soporte para bases de datos relacionales
- Interfaz web
- Soporte para múltiples tablas
- Métricas de rendimiento en tiempo real
- Mejor manejo de consultas complejas
