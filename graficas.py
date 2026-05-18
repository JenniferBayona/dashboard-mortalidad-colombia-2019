import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def mapa_muertes_departamento(df):
    ruta_geojson = DATA_DIR / "Colombia.geojson"
    if df.empty or not ruta_geojson.exists():
        return px.scatter(title="Sin datos para el mapa")
    with open(ruta_geojson, "r", encoding="utf-8") as archivo:
        geojson_colombia = json.load(archivo)
    muertes_dpto = df.groupby("COD_DEPARTAMENTO").size().reset_index(name="total_muertes")
    fig = px.choropleth(muertes_dpto, geojson=geojson_colombia, locations="COD_DEPARTAMENTO", featureidkey="properties.DPTO", color="total_muertes", color_continuous_scale="Reds", title="Distribución Geográfica")
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    return fig

def grafico_evolucion_mensual(df):
    if df.empty or "MES" not in df.columns: return px.scatter(title="Sin datos de meses")
    muertes_mes = df.groupby("MES").size().reset_index(name="Total")
    meses_map = {1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"}
    muertes_mes["Nombre_Mes"] = muertes_mes["MES"].map(meses_map)
    muertes_mes = muertes_mes.sort_values("MES")
    fig = px.line(muertes_mes, x="Nombre_Mes", y="Total", title="Evolución Mensual de Defunciones", markers=True, color_discrete_sequence=["#2E86C1"])
    fig.update_traces(hovertemplate="<b>Mes:</b> %{x}<br><b>Defunciones:</b> %{y:,}<extra></extra>", line=dict(width=3), marker=dict(size=8, symbol="circle"))
    fig.update_layout(xaxis_title="", yaxis_title="Casos", margin={"r": 10, "t": 40, "l": 10, "b": 10}, xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True))
    return fig

def grafico_causas_muerte(df):
    if df.empty: return px.scatter(title="Sin datos")
    df_plot = df.copy()
    df_plot["CAUSA_LIMPIA"] = df_plot["CAUSA_MUERTE_DETALLE"].str.replace(r"(?i)(,?\s*no especificad[oa]s?|,?\s*sin otra especificaci[oó]n)", "", regex=True).str.strip()
    conteo_causas = df_plot["CAUSA_LIMPIA"].value_counts().nlargest(10).reset_index()
    conteo_causas.columns = ["CAUSA_LIMPIA", "Total"]
    conteo_causas["ID_Causa"] = ["Causa " + str(i+1) for i in range(len(conteo_causas))]
    df_top = df_plot[df_plot["CAUSA_LIMPIA"].isin(conteo_causas["CAUSA_LIMPIA"])]
    dept_counts = df_top.groupby(["CAUSA_LIMPIA", "DEPARTAMENTO"]).size().reset_index(name="Muertes")
    dept_counts = dept_counts.sort_values(["CAUSA_LIMPIA", "Muertes"], ascending=[True, False])
    def top3_a_texto(grupo): return "<br>".join([f"  • {row['DEPARTAMENTO']}: {row['Muertes']} casos" for _, row in grupo.head(3).iterrows()])
    top_deptos_txt = dept_counts.groupby("CAUSA_LIMPIA").apply(top3_a_texto).reset_index(name="Top_Departamentos")
    df_final = pd.merge(conteo_causas, top_deptos_txt, on="CAUSA_LIMPIA")
    fig = px.bar(df_final, x="ID_Causa", y="Total", title="Top 10 Causas de Muerte (Pasa el cursor)", text="Total", custom_data=["Top_Departamentos", "CAUSA_LIMPIA"], color="Total", color_continuous_scale="Viridis")
    fig.update_traces(hovertemplate="<b>%{customdata[1]}</b><br><br>Casos: %{y:,}<br><br><b>Top Departamentos:</b><br>%{customdata[0]}<extra></extra>", textposition="outside")
    fig.update_layout(xaxis={'title': '', 'fixedrange': True, 'showticklabels': False}, yaxis={'title': '', 'fixedrange': True}, showlegend=False, margin={"r": 10, "t": 40, "l": 10, "b": 20}, coloraxis_showscale=False)
    return fig

def grafico_top_ciudades_violentas(df):
    if df.empty: return px.scatter(title="Sin datos")
    df_violencia = df[df["COD_MUERTE"].astype(str).str.startswith("X95", na=False)]
    if df_violencia.empty: return px.scatter(title="Sin homicidios por arma de fuego (X95) en el filtro")
    top_ciudades = df_violencia.groupby("MUNICIPIO").size().reset_index(name="Total").nlargest(5, "Total").sort_values("Total", ascending=True)
    fig = px.bar(top_ciudades, x="Total", y="MUNICIPIO", orientation='h', title="Top 5 Ciudades: Homicidios Arma de Fuego", text="Total", color="Total", color_continuous_scale="Reds")
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Homicidios: %{x:,}<extra></extra>", textposition="outside")
    fig.update_layout(xaxis={'title': '', 'fixedrange': True, 'showticklabels': False}, yaxis={'title': '', 'fixedrange': True}, showlegend=False, margin={"r": 10, "t": 40, "l": 10, "b": 20}, coloraxis_showscale=False)
    return fig

def grafico_distribucion_genero(df):
    if df.empty: return px.scatter(title="Sin datos")
    fig = px.pie(df, names="SEXO_DESC", title="Distribución por Género", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(hovertemplate="<b>%{label}</b><br>Casos: %{value:,}<br>Porcentaje: %{percent}<extra></extra>")
    fig.update_layout(margin={"r": 10, "t": 40, "l": 10, "b": 10})
    return fig

def grafico_menor_mortalidad(df):
    if df.empty: return px.scatter(title="Sin datos")
    top_menor = df.groupby("MUNICIPIO").size().reset_index(name="Total").nsmallest(10, "Total")
    fig = px.pie(top_menor, names="MUNICIPIO", values="Total", title="10 Ciudades con Menor Mortalidad", color_discrete_sequence=px.colors.sequential.Teal)
    fig.update_traces(hovertemplate="<b>%{label}</b><br>Casos: %{value:,}<extra></extra>")
    fig.update_layout(margin={"r": 10, "t": 40, "l": 10, "b": 10})
    return fig

def tabla_top_causas(df):
    if df.empty: return px.scatter(title="Sin datos")
    top_causas = df.groupby(["COD_MUERTE", "CAUSA_MUERTE_DETALLE"]).size().reset_index(name="Total").nlargest(10, "Total")
    fig = go.Figure(data=[go.Table(
        header=dict(values=['<b>CÓDIGO</b>', '<b>CAUSA DE MUERTE</b>', '<b>TOTAL CASOS</b>'], fill_color='#2E86C1', font=dict(color='white', size=12), align='left'),
        cells=dict(values=[top_causas['COD_MUERTE'], top_causas['CAUSA_MUERTE_DETALLE'], top_causas['Total']], fill_color='#F2F3F4', align='left', format=[None, None, ","])
    )])
    fig.update_layout(title="Tabla de Referencia: Top 10 Causas", margin={"r": 0, "t": 40, "l": 0, "b": 0})
    return fig

def grafico_sexo_departamento(df):
    if df.empty: return px.scatter(title="Sin datos")
    agrupado = df.groupby(["DEPARTAMENTO", "SEXO_DESC"]).size().reset_index(name="Total")
    
    # SOLUCIÓN: Agregamos el diccionario 'labels' para traducir las variables a lenguaje humano
    fig = px.bar(
        agrupado, x="DEPARTAMENTO", y="Total", color="SEXO_DESC", 
        title="Comparación por Género en cada Departamento", barmode="stack", 
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"SEXO_DESC": "Género", "DEPARTAMENTO": "Departamento", "Total": "Casos"}
    )
    
    fig.update_layout(xaxis={'categoryorder': 'total descending', 'title': ''}, yaxis_title="Total de Casos", margin={"r": 10, "t": 40, "l": 10, "b": 40}, legend_title_text="Género")
    return fig

def grafico_histograma_edad(df):
    if df.empty or "GRUPO_EDAD1" not in df.columns: return px.scatter(title="Sin datos de Edad")
    df_plot = df.copy()
    df_plot["GRUPO_EDAD1"] = df_plot["GRUPO_EDAD1"].astype(str)
    
    fig = px.histogram(
        df_plot, x="GRUPO_EDAD1", title="Distribución por Grupo de Edad (Ciclo de Vida)", 
        color_discrete_sequence=["#8E44AD"]
    )
    
    # SOLUCIÓN: Ocultamos los nombres técnicos y aplicamos formato de miles al Tooltip
    fig.update_traces(hovertemplate="<b>Edad: %{x}</b><br>Casos: %{y:,}<extra></extra>")
    fig.update_layout(xaxis={'categoryorder': 'category ascending', 'title': 'Código DANE del Rango de Edad'}, yaxis_title="Total de Casos", margin={"r": 10, "t": 40, "l": 10, "b": 10})
    return fig