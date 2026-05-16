import json
import plotly.express as px
from carga_datos import mortalidad


def mapa_muertes_departamento(mortalidad, ruta_geojson="data/Colombia.geojson"):

    with open(ruta_geojson, "r", encoding="utf-8") as archivo:
        geojson_colombia = json.load(archivo)

    muertes_dpto = (mortalidad.groupby("COD_DEPARTAMENTO").size().reset_index(name="total_muertes"))

    muertes_dpto["COD_DEPARTAMENTO"] = (muertes_dpto["COD_DEPARTAMENTO"].astype(str).str.zfill(2))

    fig = px.choropleth(
        muertes_dpto,
        geojson=geojson_colombia,
        locations="COD_DEPARTAMENTO",
        featureidkey="properties.DPTO",
        color="total_muertes",
        color_continuous_scale="Reds",
        title="Distribución total de muertes por departamento en Colombia - 2019",
        labels={
            "total_muertes": "Total de muertes",
            "COD_DEPARTAMENTO": "Departamento"
        }
    )

    fig.update_geos(fitbounds="locations", visible=False)

    fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})

    return fig

if __name__ == "__main__":
    fig = mapa_muertes_departamento(mortalidad)
    fig.show()