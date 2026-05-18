import dash
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import os

from carga_datos import mortalidad, obtener_metricas_kpi
from graficas import (
    mapa_muertes_departamento, grafico_evolucion_mensual, grafico_causas_muerte, 
    grafico_top_ciudades_violentas, grafico_distribucion_genero,
    grafico_menor_mortalidad, tabla_top_causas, grafico_sexo_departamento, grafico_histograma_edad
)

# Configuración de opciones de filtros
opciones_deptos = [{"label": "Todos los Departamentos", "value": "TODOS"}] + \
                  [{"label": str(dpto), "value": str(dpto)} for dpto in sorted(mortalidad["DEPARTAMENTO"].dropna().unique())]

opciones_manera = [{"label": "Todas las Maneras", "value": "TODAS"}] + \
                  [{"label": str(m), "value": str(m)} for m in sorted(mortalidad["MANERA_MUERTE"].dropna().unique())]

# NUEVO: Filtro exigido por la guía de actividades
opciones_sexo = [{"label": "Todos los Géneros", "value": "TODOS"}] + \
                [{"label": str(s), "value": str(s)} for s in sorted(mortalidad["SEXO_DESC"].dropna().unique())]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    html.H1("Dashboard Avanzado de Mortalidad - Colombia 2019", className="text-center mt-4 mb-2 fw-bold text-primary"),
    html.P("Panel integral interactivo - Maestría en Inteligencia Artificial", className="text-center text-muted mb-4"),

    # SECCIÓN DE FILTROS (Se añade el tercer filtro de género)
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Filtrar por Departamento:", className="fw-bold"),
                    dcc.Dropdown(id="filtro-depto", options=opciones_deptos, value="TODOS", clearable=False)
                ], md=4),
                dbc.Col([
                    html.Label("Filtrar por Manera de Muerte:", className="fw-bold"),
                    dcc.Dropdown(id="filtro-manera", options=opciones_manera, value="TODAS", clearable=False)
                ], md=4),
                dbc.Col([
                    html.Label("Filtrar por Género:", className="fw-bold"),
                    dcc.Dropdown(id="filtro-sexo", options=opciones_sexo, value="TODOS", clearable=False)
                ], md=4),
            ])
        ])
    ], className="mb-4 shadow-sm"),

    # TARJETAS KPI
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.H5("Total Casos", className="text-muted"), html.H2(id="kpi-registros", className="fw-bold text-danger")]), className="text-center shadow-sm"), md=4),
        dbc.Col(dbc.Card(dbc.CardBody([html.H5("Departamentos", className="text-muted"), html.H2(id="kpi-deptos", className="fw-bold text-success")]), className="text-center shadow-sm"), md=4),
        dbc.Col(dbc.Card(dbc.CardBody([html.H5("Municipios Afectados", className="text-muted"), html.H2(id="kpi-municipios", className="fw-bold text-warning")]), className="text-center shadow-sm"), md=4),
    ], className="mb-4"),

    # DISTRIBUCIÓN DE LAS 9 GRÁFICAS EN CUADRÍCULA (Para nota máxima en Estilo)
    dbc.Row([
        dbc.Col(dcc.Graph(id="mapa-mortalidad"), md=6, className="mb-4"),
        dbc.Col(dcc.Graph(id="grafico-edad"), md=6, className="mb-4"),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="grafico-lineas"), md=6, className="mb-4"),
        dbc.Col(dcc.Graph(id="grafico-sexo-depto"), md=6, className="mb-4"),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="grafico-causas"), md=6, className="mb-4"),
        dbc.Col(dcc.Graph(id="tabla-causas"), md=6, className="mb-4"),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="grafico-ciudades"), md=4, className="mb-4"),
        dbc.Col(dcc.Graph(id="grafico-menor-mortalidad"), md=4, className="mb-4"),
        dbc.Col(dcc.Graph(id="grafico-genero"), md=4, className="mb-4"),
    ]),

], fluid=True)

@app.callback(
    [Output("kpi-registros", "children"), Output("kpi-deptos", "children"), Output("kpi-municipios", "children"),
     Output("mapa-mortalidad", "figure"), Output("grafico-edad", "figure"),
     Output("grafico-lineas", "figure"), Output("grafico-sexo-depto", "figure"),
     Output("grafico-causas", "figure"), Output("tabla-causas", "figure"),
     Output("grafico-ciudades", "figure"), Output("grafico-menor-mortalidad", "figure"),
     Output("grafico-genero", "figure")],
    [Input("filtro-depto", "value"), Input("filtro-manera", "value"), Input("filtro-sexo", "value")]
)
def actualizar_dashboard(depto_seleccionado, manera_seleccionada, sexo_seleccionado):
    df_filtrado = mortalidad.copy()
    
    # Aplicación de los 3 filtros cruzados en cascada
    if depto_seleccionado != "TODOS": 
        df_filtrado = df_filtrado[df_filtrado["DEPARTAMENTO"] == depto_seleccionado]
    if manera_seleccionada != "TODAS": 
        df_filtrado = df_filtrado[df_filtrado["MANERA_MUERTE"] == manera_seleccionada]
    if sexo_seleccionado != "TODOS": 
        df_filtrado = df_filtrado[df_filtrado["SEXO_DESC"] == sexo_seleccionado]
        
    tot_reg, tot_depto, tot_muni = obtener_metricas_kpi(df_filtrado)
    kpi1, kpi2, kpi3 = f"{tot_reg:,}", str(tot_depto), f"{tot_muni:,}"
    
    # Construcción de gráficos estructurados
    return (
        kpi1, kpi2, kpi3,
        mapa_muertes_departamento(df_filtrado),
        grafico_histograma_edad(df_filtrado),
        grafico_evolucion_mensual(df_filtrado),
        grafico_sexo_departamento(df_filtrado),
        grafico_causas_muerte(df_filtrado),
        tabla_top_causas(df_filtrado),
        grafico_top_ciudades_violentas(df_filtrado),
        grafico_menor_mortalidad(df_filtrado),
        grafico_distribucion_genero(df_filtrado)
    )

if __name__ == "__main__":
    app.run(debug=False)