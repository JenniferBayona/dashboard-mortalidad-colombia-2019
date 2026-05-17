import pandas as pd
import os

# Ubicamos la carpeta data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def cargar_y_limpiar_mortalidad():
    print("⏳ Iniciando la carga y transformación de datos en el Backend...")
    
    # Rutas con los nombres EXACTOS que nos dio tu consola (Formato Excel)
    ruta_mortalidad = os.path.join(DATA_DIR, "NoFetal2019.xlsx")
    ruta_cie10 = os.path.join(DATA_DIR, "CodigosDeMuerte.xlsx")
    ruta_divipola = os.path.join(DATA_DIR, "Divipola.xlsx")

    # 1. Carga de datos usando el motor de Excel
    # (Usamos engine='openpyxl' para garantizar lectura de archivos modernos)
    df_mortalidad = pd.read_excel(ruta_mortalidad, engine='openpyxl')
    df_cie10 = pd.read_excel(ruta_cie10, engine='openpyxl')
    df_divipola = pd.read_excel(ruta_divipola, engine='openpyxl')

    # Limpiamos posibles espacios en blanco en los nombres de las columnas
    df_mortalidad.columns = df_mortalidad.columns.str.strip()
    df_cie10.columns = df_cie10.columns.str.strip()
    df_divipola.columns = df_divipola.columns.str.strip()

    # 2. Transformación ETL: Estandarización de Códigos DANE
    df_mortalidad["COD_DEPARTAMENTO"] = df_mortalidad["COD_DEPARTAMENTO"].astype(str).str.zfill(2)
    df_mortalidad["COD_MUNICIPIO"] = df_mortalidad["COD_MUNICIPIO"].astype(str).str.zfill(3)
    
    # 3. Homologación semántica (Traducción de sexo)
    df_mortalidad["SEXO"] = pd.to_numeric(df_mortalidad["SEXO"], errors='coerce')
    mapeo_sexo = {1: "Masculino", 2: "Femenino", 3: "Indeterminado", 9: "Sin Información"}
    df_mortalidad["SEXO_DESC"] = df_mortalidad["SEXO"].map(mapeo_sexo).fillna("No Especificado")

    # 4. Enriquecimiento de Datos (Left Joins)
    col_codigo_cie = df_cie10.columns[4]
    col_desc_cie = df_cie10.columns[5]

    df_enriquecido = pd.merge(
        df_mortalidad,
        df_cie10[[col_codigo_cie, col_desc_cie]],
        left_on="COD_MUERTE",
        right_on=col_codigo_cie,
        how="left"
    ).rename(columns={col_desc_cie: "CAUSA_MUERTE_DETALLE"})

    df_divipola["COD_DEPARTAMENTO"] = df_divipola["COD_DEPARTAMENTO"].astype(str).str.zfill(2)
    df_divipola["COD_MUNICIPIO"] = df_divipola["COD_MUNICIPIO"].astype(str).str.zfill(3)
    
    df_final = pd.merge(
        df_enriquecido,
        df_divipola[["COD_DEPARTAMENTO", "DEPARTAMENTO", "COD_MUNICIPIO", "MUNICIPIO"]].drop_duplicates(),
        on=["COD_DEPARTAMENTO", "COD_MUNICIPIO"],
        how="left"
    )
    
    return df_final

def obtener_metricas_kpi(df):
    if df is None or df.empty:
        return 0, 0, 0
    total_registros = len(df)
    total_departamentos = df["COD_DEPARTAMENTO"].nunique() if "COD_DEPARTAMENTO" in df.columns else 0
    total_municipios = df["COD_MUNICIPIO"].nunique() if "COD_MUNICIPIO" in df.columns else 0
    return total_registros, total_departamentos, total_municipios

# Ejecución
try:
    mortalidad = cargar_y_limpiar_mortalidad()
    if not mortalidad.empty:
        print("🚀 Backend operativo: Pipeline completado con éxito. Datos listos.")
except Exception as e:
    print(f"❌ Error crítico en el pipeline de datos: {e}")
    mortalidad = pd.DataFrame()