import plotly.express as px
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc

# Importamos tu backend y la función del mapa
from carga_datos import mortalidad, obtener_metricas_kpi
from graficas import mapa_muertes_departamento

# 1. Inicialización de métricas y gráficos
total_reg, total_depto, total_muni = obtener_metricas_kpi(mortalidad)
fig_mapa = mapa_muertes_departamento(mortalidad)

# 2. Creación de la aplicación Web
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# 3. Layout de la interfaz gráfica
app.layout = dbc.Container([
    
    # Encabezado
    html.H1("Dashboard de Mortalidad en Colombia - 2019", className="text-center mt-4 mb-3 fw-bold text-primary"),
    html.P("Plataforma analítica para la exploración de patrones de defunción a nivel nacional.", className="text-center text-muted mb-4"),

    # Tarjetas de KPIs Dinámicas
    dbc.Row([
        dbc.Col([dbc.Card([dbc.CardBody([html.H6("Total de Registros", className="card-title text-secondary"), html.H2(f"{total_reg:,}", className="fw-bold text-dark")])], color="light", outline=True)], md=4),
        dbc.Col([dbc.Card([dbc.CardBody([html.H6("Departamentos", className="card-title text-secondary"), html.H2(str(total_depto), className="fw-bold text-danger")])], color="light", outline=True)], md=4),
        dbc.Col([dbc.Card([dbc.CardBody([html.H6("Municipios", className="card-title text-secondary"), html.H2(f"{total_muni:,}", className="fw-bold text-info")])], color="light", outline=True)], md=4),
    ], className="mb-4"),

    html.Hr(className="mb-4"),

    # Sección de Gráficos (Distribución en 2 columnas)
    dbc.Row([
        # Columna Izquierda: Mapa
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_mapa)
                ])
            ], className="shadow-sm")
        ], md=6),
        
        # Columna Derecha: Histograma
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        figure=px.histogram(
                            mortalidad, 
                            x="SEXO_DESC" if not mortalidad.empty else None, 
                            title="Distribución Absoluta por Género",
                            labels={"SEXO_DESC": "Género", "count": "Número de Casos"},
                            color="SEXO_DESC" if not mortalidad.empty else None,
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        ) if not mortalidad.empty else px.scatter(title="Esperando datos...")
                    )
                ])
            ], className="shadow-sm")
        ], md=6)
    ])

], fluid=True, className="p-4 bg-light")

# 4. Ejecución del servidor local
if __name__ == "__main__":
    app.run(debug=True)