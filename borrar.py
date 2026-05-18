import json
import plotly.express as px


with open("data/Colombia.geojson", "r", encoding="utf-8") as archivo:
    geojson_colombia = json.load(archivo)

print(geojson_colombia.keys())

print(geojson_colombia["features"][0].keys())

print(geojson_colombia["features"][0]["properties"])


def mapa_departamentos(df):

    with open("Colombia.geojson", "r", encoding="utf-8") as archivo:
        geojson_colombia = json.load(archivo)

    # Contar muertes por departamento
    muertes = (
        df.groupby("COD_DPTO")
        .size()
        .reset_index(name="total_muertes")
    )

    # Convertir códigos a texto
    muertes["COD_DPTO"] = (
        muertes["COD_DPTO"]
        .astype(str)
        .str.zfill(2)
    )

    fig = px.choropleth(
        muertes,
        geojson=geojson_colombia,
        locations="COD_DPTO",
        featureidkey="properties.DPTO_CCDGO",
        color="total_muertes",
        hover_name="COD_DPTO",
        color_continuous_scale="Reds",
        title="Muertes por departamento"
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    return fig