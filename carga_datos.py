import pandas as pd
import os

# 1. Configuración de Rutas del Proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def cargar_y_limpiar_mortalidad():
    print("⏳ Iniciando la carga de datos desde archivos binarios Feather...")
    
    # Rutas a los archivos binarios altamente optimizados para la nube
    ruta_mortalidad = os.path.join(DATA_DIR, "NoFetal2019.feather")
    ruta_cie10 = os.path.join(DATA_DIR, "CodigosDeMuerte.feather")
    ruta_divipola = os.path.join(DATA_DIR, "Divipola.feather")

    # Verificar si los archivos .feather existen antes de intentar leerlos
    # Si no existen, intenta cargarlos desde los .xlsx originales locales
    if not (os.path.exists(ruta_mortalidad) and os.path.exists(ruta_cie10) and os.path.exists(ruta_divipola)):
        print("⚠️ No se encontraron los archivos .feather. Intentando leer desde .xlsx originales...")
        try:
            ruta_m_xlsx = os.path.join(DATA_DIR, "NoFetal2019.xlsx")
            ruta_c_xlsx = os.path.join(DATA_DIR, "CodigosDeMuerte.xlsx")
            ruta_d_xlsx = os.path.join(DATA_DIR, "Divipola.xlsx")
            
            df_mortalidad = pd.read_excel(ruta_m_xlsx, engine='openpyxl')
            df_cie10 = pd.read_excel(ruta_c_xlsx, engine='openpyxl')
            df_divipola = pd.read_excel(ruta_d_xlsx, engine='openpyxl')
            
            # Limpiamos posibles espacios en blanco en los nombres de las columnas antes de guardar
            df_mortalidad.columns = df_mortalidad.columns.str.strip()
            df_cie10.columns = df_cie10.columns.str.strip()
            df_divipola.columns = df_divipola.columns.str.strip()

            print("💾 Guardando copias en formato .feather para optimizar futuros arranques...")
            df_mortalidad.to_feather(ruta_mortalidad)
            df_cie10.to_feather(ruta_cie10)
            df_divipola.to_feather(ruta_divipola)
        except Exception as e:
            raise FileNotFoundError(f"Error crítico al intentar procesar los archivos de datos: {e}")
    else:
        # La lectura nativa ultraveloz que usará Render
        df_mortalidad = pd.read_feather(ruta_mortalidad)
        df_cie10 = pd.read_feather(ruta_cie10)
        df_divipola = pd.read_feather(ruta_divipola)

    # Asegurar limpieza de columnas nuevamente por seguridad
    df_mortalidad.columns = df_mortalidad.columns.str.strip()
    df_cie10.columns = df_cie10.columns.str.strip()
    df_divipola.columns = df_divipola.columns.str.strip()

    # 3. Mapeo de Diccionarios y Traducción de Variables
    sexo_map = {1: "MASCULINO", 2: "FEMENINO", 3: "INDETERMINADO", 9: "SIN REGISTRO"}
    est_civil_map = {
        1: "SOLTERO(A)", 2: "CASADO(A)", 3: "UNIÓN LIBRE", 
        4: "VIUDO(A)", 5: "DIVORCIADO(A)", 6: "SEPARADO(A)", 9: "SIN REGISTRO"
    }

    df_mortalidad["SEXO_DESC"] = df_mortalidad["SEXO"].map(sexo_map).fillna("No Especificado")
    
    # CORRECCIÓN AQUÍ: Se cambió 'EST_CIVIL' por 'ESTADO_CIVIL' para coincidir con tu Excel original
    if "ESTADO_CIVIL" in df_mortalidad.columns:
        df_mortalidad["EST_CIVIL_DESC"] = df_mortalidad["ESTADO_CIVIL"].map(est_civil_map).fillna("No Especificado")
    elif "EST_CIVIL" in df_mortalidad.columns:
        df_mortalidad["EST_CIVIL_DESC"] = df_mortalidad["EST_CIVIL"].map(est_civil_map).fillna("No Especificado")
    else:
        df_mortalidad["EST_CIVIL_DESC"] = "No Especificado"

    # Normalización de Llaves para los Cruces (Formateo de Cadenas)
    df_mortalidad["COD_MUERTE"] = df_mortalidad["COD_MUERTE"].astype(str).str.strip()
    df_mortalidad["COD_DEPARTAMENTO"] = df_mortalidad["COD_DEPARTAMENTO"].astype(str).str.zfill(2)
    df_mortalidad["COD_MUNICIPIO"] = df_mortalidad["COD_MUNICIPIO"].astype(str).str.zfill(3)

    # 4. Enriquecimiento de Datos: Cruce CIE-10 (Causas de Muerte)
    col_codigo_cie = df_cie10.columns[4]  # Código de la CIE-10 cuatro caracteres
    col_desc_cie = df_cie10.columns[5]    # Descripción de códigos mortalidad a cuatro caracteres

    df_cie10[col_codigo_cie] = df_cie10[col_codigo_cie].astype(str).str.strip()

    df_enriquecido = pd.merge(
        df_mortalidad,
        df_cie10[[col_codigo_cie, col_desc_cie]],
        left_on="COD_MUERTE",
        right_on=col_codigo_cie,
        how="left"
    ).rename(columns={col_desc_cie: "CAUSA_MUERTE_DETALLE"})

    # 5. Enriquecimiento de Datos: Cruce Divipola (Nombres Geográficos)
    df_divipola["COD_DEPARTAMENTO"] = df_divipola["COD_DEPARTAMENTO"].astype(str).str.zfill(2)
    df_divipola["COD_MUNICIPIO"] = df_divipola["COD_MUNICIPIO"].astype(str).str.zfill(3)
    
    df_final = pd.merge(
        df_enriquecido,
        df_divipola[["COD_DEPARTAMENTO", "DEPARTAMENTO", "COD_MUNICIPIO", "MUNICIPIO"]].drop_duplicates(),
        on=["COD_DEPARTAMENTO", "COD_MUNICIPIO"],
        how="left"
    )
    
    print("🚀 Backend operativo: Pipeline completado con éxito. Datos listos.")
    return df_final

def obtener_metricas_kpi(df):
    """Calcula las métricas principales para las tarjetas KPI de Dash"""
    if df is None or df.empty:
        return 0, 0, 0
    total_registros = len(df)
    total_departamentos = df["COD_DEPARTAMENTO"].nunique() if "COD_DEPARTAMENTO" in df.columns else 0
    total_municipios = df["COD_MUNICIPIO"].nunique() if "COD_MUNICIPIO" in df.columns else 0
    return total_registros, total_departamentos, total_municipios

# Ejecución Inicial Automática al importar el archivo
mortalidad = cargar_y_limpiar_mortalidad()