import dash
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

from carga_datos import mortalidad, obtener_metricas_kpi
# Importamos todas las 9 funciones gráficas
from graficas import (
    mapa_muertes_departamento, grafico_evolucion_mensual, grafico_causas_muerte, 
    grafico_top_ciudades_violentas, grafico_distribucion_genero,
    grafico_menor_mortalidad, tabla_top_causas, grafico_sexo_departamento, grafico_histograma_edad
)

opciones_deptos = [{"label": "Todos los Departamentos", "value": "TODOS"}] + \
                  [{"label": str(dpto), "value": str(dpto)} for dpto in sorted(mortalidad["DEPARTAMENTO"].dropna().unique())]
opciones_manera = [{"label": "Todas", "value": "TODAS"}] + \
                  [{"label": str(m), "value": str(m)} for m in sorted(mortalidad["MANERA_MUERTE"].dropna().unique())]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    html.H1("Dashboard Avanzado de Mortalidad - Colombia 2019", className="text-center mt-4 mb-2 fw-bold text-primary"),
    html.P("Panel integral interactivo.", className="text-center text-muted mb-4"),

    # FILTROS
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([html.Label("Departamento:", className="fw-bold"), dcc.Dropdown(id="filtro-depto", options=opciones_deptos, value="TODOS", clearable=False)], md=6),
                dbc.Col([html.Label("Manera de Muerte:", className="fw-bold"), dcc.Dropdown(id="filtro-manera", options=opciones_manera, value="TODAS", clearable=False)], md=6),
            ])
        ])
    ], className="mb-4 shadow-sm"),

    # KPIS
    dbc.Row([
        dbc.Col([dbc.Card([dbc.CardBody([html.H6("Registros", className="text-secondary"), html.H3(id="kpi-reg", className="text-primary")])])], md=4),
        dbc.Col([dbc.Card([dbc.CardBody([html.H6("Departamentos", className="text-secondary"), html.H3(id="kpi-depto", className="text-danger")])])], md=4),
        dbc.Col([dbc.Card([dbc.CardBody([html.H6("Municipios", className="text-secondary"), html.H3(id="kpi-muni", className="text-info")])])], md=4),
    ], className="mb-4"),

    # FILA 1: Mapa e Histograma de Edad
    dbc.Row([
        dbc.Col([dbc.Card([dbc.CardBody([dcc.Graph(id="grafico-mapa")])], className="shadow-sm mb-4")], md=6),
        dbc.Col([dbc.Card([dbc.CardBody([dcc.Graph(id="grafico-edad")])], className="shadow-sm mb-4")], md=6), 
    ]),

    # FILA 2: Evolución Mensual y Barras Apiladas por Género
    dbc.Row([
        dbc.Col([dbc.Card([dbc.CardBody([dcc.Graph(id="grafico-lineas")])], className="shadow-sm mb-4")], md=5),
        dbc.Col([dbc.Card([dbc.CardBody([dcc.Graph(id="grafico-sexo-depto")])], className="shadow-sm mb-4")], md=7),
    ]),
    
    # FILA 3: Top Causas (Gráfica) y Tabla de Causas
    dbc.Row([
        dbc.Col([dbc.Card([dbc.CardBody([dcc.Graph(id="grafico-causas")])], className="shadow-sm mb-4")], md=6),
        dbc.Col([dbc.Card([dbc.CardBody([dcc.Graph(id="tabla-causas")])], className="shadow-sm mb-4")], md=6),
    ]),

    # FILA 4: Ciudades Violentas, Menor Mortalidad y Género General
    dbc.Row([
        dbc.Col([dbc.Card([dbc.CardBody([dcc.Graph(id="grafico-ciudades")])], className="shadow-sm")], md=4),
        dbc.Col([dbc.Card([dbc.CardBody([dcc.Graph(id="grafico-menor-mortalidad")])], className="shadow-sm")], md=4),
        dbc.Col([dbc.Card([dbc.CardBody([dcc.Graph(id="grafico-genero")])], className="shadow-sm")], md=4)
    ], className="mb-4")

], fluid=True, className="p-4 bg-light")

@app.callback(
    [Output("kpi-reg", "children"), Output("kpi-depto", "children"), Output("kpi-muni", "children"),
     Output("grafico-mapa", "figure"), Output("grafico-edad", "figure"),
     Output("grafico-lineas", "figure"), Output("grafico-sexo-depto", "figure"),
     Output("grafico-causas", "figure"), Output("tabla-causas", "figure"),
     Output("grafico-ciudades", "figure"), Output("grafico-menor-mortalidad", "figure"),
     Output("grafico-genero", "figure")],
    [Input("filtro-depto", "value"), Input("filtro-manera", "value")]
)
def actualizar_dashboard(depto_seleccionado, manera_seleccionada):
    df_filtrado = mortalidad.copy()
    if depto_seleccionado != "TODOS": df_filtrado = df_filtrado[df_filtrado["DEPARTAMENTO"] == depto_seleccionado]
    if manera_seleccionada != "TODAS": df_filtrado = df_filtrado[df_filtrado["MANERA_MUERTE"] == manera_seleccionada]
        
    tot_reg, tot_depto, tot_muni = obtener_metricas_kpi(df_filtrado)
    kpi1, kpi2, kpi3 = f"{tot_reg:,}", str(tot_depto), f"{tot_muni:,}"
    
    # Generamos las 9 gráficas simultáneamente
    fig_mapa = mapa_muertes_departamento(df_filtrado)
    fig_edad = grafico_histograma_edad(df_filtrado)
    fig_lineas = grafico_evolucion_mensual(df_filtrado) 
    fig_sexo_depto = grafico_sexo_departamento(df_filtrado)
    fig_causas = grafico_causas_muerte(df_filtrado)
    fig_tabla = tabla_top_causas(df_filtrado)
    fig_ciudades = grafico_top_ciudades_violentas(df_filtrado) 
    fig_menor_mort = grafico_menor_mortalidad(df_filtrado)
    fig_genero = grafico_distribucion_genero(df_filtrado)
    
    return kpi1, kpi2, kpi3, fig_mapa, fig_edad, fig_lineas, fig_sexo_depto, fig_causas, fig_tabla, fig_ciudades, fig_menor_mort, fig_genero

if __name__ == "__main__":
    app.run(debug=True)