#Eliminar la columna de sql_original y cambiar el nombre de sql_corregido a sql
import pandas as pd

df = pd.read_csv("data/stage/consultas_resueltas.csv", sep="\t", encoding="latin-1")
df = df.drop(columns=["SQL_Original"]) 
df = df.rename(columns={"SQL_Corregido": "SQL"})

df.to_csv("data/stage/consultas_resueltas_final.csv", sep="\t", encoding="latin-1", index=False)