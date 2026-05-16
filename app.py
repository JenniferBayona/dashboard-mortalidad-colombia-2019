import plotly.express as px
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from carga_datos import mortalidad


# CREACIÓN DE LA APP

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server  # Necesario para desplegar en Render

# LAYOUT

app.layout = dbc.Container([
    
    html.H1("Dashboard de Mortalidad en Colombia - 2019", className="text-center mt-4 mb-4"),

    html.P("Aplicación web interactiva desarrollada con Python, Dash y Plotly " \
    "para analizar patrones de mortalidad en Colombia durante el año 2019.", className="text-center"),

    dbc.Row([
        dbc.Col([dbc.Card([dbc.CardBody([html.H4("Total de registros"), html.H2("5")])])], md=4),

        dbc.Col([dbc.Card([dbc.CardBody([html.H4("Departamentos"), html.H2("32")])])], md=4),

        dbc.Col([dbc.Card([dbc.CardBody([html.H4("Municipios"),html.H2("1,022")])])], md=4),
    ], className="mb-4"),

    html.Hr(),

    html.H3("Primer gráfico de prueba"),

    dcc.Graph(figure=px.histogram(mortalidad, x="SEXO", title="Distribución de muertes por sexo"))

], fluid=True)

# EJECUCIÓN LOCAL

if __name__ == "__main__":
    app.run(debug=True)