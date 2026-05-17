import json
import plotly.express as px
from pathlib import Path

# Configuración de rutas robusta
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def mapa_muertes_departamento(df_mortalidad):
    """Genera un mapa coroplético de Colombia basado en el GeoJSON."""
    ruta_geojson = DATA_DIR / "Colombia.geojson"
    
    # Si la tabla está vacía o el archivo GeoJSON no existe, devolvemos un gráfico vacío
    if df_mortalidad.empty or not ruta_geojson.exists():
        return px.scatter(title="Mapa no disponible: Faltan datos o archivo GeoJSON")

    with open(ruta_geojson, "r", encoding="utf-8") as archivo:
        geojson_colombia = json.load(archivo)

    # Agrupamos los datos por departamento para el mapa
    muertes_dpto = df_mortalidad.groupby("COD_DEPARTAMENTO").size().reset_index(name="total_muertes")

    # Creamos el mapa
    fig = px.choropleth(
        muertes_dpto,
        geojson=geojson_colombia,
        locations="COD_DEPARTAMENTO",
        featureidkey="properties.DPTO",
        color="total_muertes",
        color_continuous_scale="Reds",
        title="Distribución Geográfica de Defunciones",
        labels={
            "total_muertes": "Total de muertes",
            "COD_DEPARTAMENTO": "Código Depto"
        }
    )

    # Ajustes estéticos del mapa
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})

    return fig