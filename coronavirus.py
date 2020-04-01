import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import dash_table_experiments
import numpy as np
import dash_table_experiments as dash_table
from dash.dependencies import Input, Output
import plotly.offline as pyo
import flask
import plotly.io as pio

import io
import requests


# df_internacional = pd.read_csv('https://docs.google.com/spreadsheets/d/1avGWWl1J19O_Zm0NGTGy2E-fOG05i4ljRfjl87P7FiA/export?gid=0&format=csv')
# 
# df_internacional['Country'] = df_internacional['Country/Region']
# df_internacional = df_internacional.groupby(['Date', 'Country/Region'], as_index=False).max()


TEMPLATE = "plotly_dark"

DF_COMUNIDADES = None
DF_WORLD = None

tabs = dbc.Container(
	[
		html.H1('Evolución Covid-19'),
		html.Div([
	        html.P('En este Dashboard se muestra la evolución del coronavirus en España y en el mundo en tiempo real. Los datos se actualizan cada media hora y la fuente oficial es Ministerio de Sanidad y consejerías autonómicas, para los datos de españa y ourworldindata.org para los datos del resto del mundo.')
	    ]),
		html.Div(
		    [
		        dbc.Tabs(
		            [
		                dbc.Tab(label="España", tab_id="espana"),
		                dbc.Tab(label="Comunidades autónomas", tab_id="comunidades"),
		                dbc.Tab(label="Internacional", tab_id="internacional"),
		            ],
		            id="tabs",
		            active_tab="espana",
		        ),
		        html.Div(id="content"),
		    ]
		)
	],
	className="mt-4 text-center",
)

def espana_layout():
	url="https://s3-eu-west-1.amazonaws.com/images.webbuildeer.com/coronavirus-total.csv"
	s=requests.get(url).content
	df_total=pd.read_csv(io.StringIO(s.decode('utf-8')))
	columns = df_total.columns.tolist()[2:]

	new = df_total['Date'].str.split(' ', n = 1, expand = True)
	df_total['Day'] = new[0]
	df_total['Hour'] = new[1]
	df_total = df_total.groupby('Day', as_index=False).max()

	df_total['nuevos_infectados'] = df_total['Casos'].diff()
	df_total['nuevas_muertes'] = df_total['Muertes'].diff()
	df_total['nuevas_altas'] = df_total['Altas'].diff()
	df_total['tasa_contagio'] = df_total['nuevos_infectados'] / (df_total['Casos'] - df_total['nuevos_infectados'])
	df_total['total_infectados'] = df_total['Casos'] - df_total['Muertes'] - df_total['Altas']

	espana = dbc.Row([
		dbc.Col(
		    [
				html.H1([dbc.Badge(str(df_total["Casos"].max()) + " Casos", className="ml-1 bg-warning")]),
			],
		    lg=4,
		    className="mt-3 mt-3"
		),
		dbc.Col(
		    [
				html.H1([dbc.Badge(str(df_total["Muertes"].max()) + " Muertes", className="ml-1 bg-danger")]),
			],
		    lg=4,
		    className="mt-3 mt-3"
		),		
		dbc.Col(
		    [
				html.H1([dbc.Badge(str(df_total["Altas"].max()) + " Altas", className="ml-1 bg-success")]),
		    ],
		    lg=4,
		    className="mt-3 mt-3"
		),
		dbc.Col(
		    [
		    	dcc.Graph(
			        id = 'Total',
			        figure = {
			            'data' : [
			                go.Scatter(
			                x = df_total['Day'],
			                y = df_total[column],
			                mode = "markers+lines",
			                name = column
			                )for column in columns


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Casos de coronavirus en España",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'}

			            )
			        }
			    )
		    ],
		    lg=12
		),
		dbc.Col(
		    [
		    	dcc.Graph(
			        id = 'Total Infectados',
			        figure = {
			            'data' : [
			                go.Scatter(
			                x = df_total['Day'],
			                y = df_total[column],
			                mode = "markers+lines",
			                name = column
			                )for column in ['total_infectados', 'Casos']


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Casos actuales en españa",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'}

			            )
			        }
			    )
		    ],
		    lg=12
		),		
		dbc.Col(
		    [
		    	dcc.Graph(
			        id = 'nuevos_infectados',
			        figure = {
			            'data' : [
			                go.Bar(

			                x = df_total['Day'],
			                y = df_total['nuevos_infectados'],
			                name = "Nuevos infectados"
			                )


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Nuevos contagiados en España",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'}

			            )
			        }
			    )
		    ],
		    lg=6,
		),
		dbc.Col(
		    [
		    	dcc.Graph(
			        id = 'tasa_contagio',
			        figure = {
			            'data' : [
			                go.Bar(

			                x = df_total['Day'],
			                y = df_total['tasa_contagio'],
			                name = "Tasa de contagios"
			                )


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Tasa de contagio en España (Casos nuevos/Casos ayer)",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'}

			            )
			        }
			    )
		    ],
		    lg=6,
		),
		dbc.Col(
		    [
		    	dcc.Graph(
			        id = 'nuevas_mertes',
			        figure = {
			            'data' : [
			                go.Bar(

			                x = df_total['Day'],
			                y = df_total['nuevas_muertes'],
			                name = "Nuevas Muertes",
			                marker = dict(
			                	color='red'
			                	)
			                )


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Nuevas Muertes en España",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'}

			            )
			        }
			    )
		    ],
		    lg=6,
		),
		dbc.Col(
		    [
		    	dcc.Graph(
			        id = 'nuevas_altas',
			        figure = {
			            'data' : [
			                go.Bar(

			                x = df_total['Day'],
			                y = df_total['nuevas_altas'],
			                name = "Nuevas Altas",
			                marker = dict(
			                	color='green'
			                	)
			                )
			             ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Nuevas Altas en España",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'},
			           

			            )
			        }
			    )
		    ],
		    lg=6,
		),

	])

	return espana


def comunidades_content(df_comunidades, values):
	scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
	    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]

	comunidades = dbc.Row([
		dbc.Col(
		    [
		    	dcc.Graph(

			        id = 'Casos_Comunidades',
			        figure = {
			            'data' : [
			                go.Scatter(

			                x = df_comunidades[df_comunidades['Comunidad'] == i]['Date'],
			                y = df_comunidades[df_comunidades['Comunidad'] == i]['Casos'],
			                mode = "markers+lines",
			                name = i
			                )for i in values

			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Casos de Coronavirus por comunidades",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'}

			            )
			        }
			    )
		    ],
		    lg=12,
		),
		dbc.Col(
		    [
		    	dcc.Graph(

			        id = 'Muertes_Comunidades',
			        figure = {
			            'data' : [
			                go.Scatter(

			                x = df_comunidades[df_comunidades['Comunidad'] == i]['Date'],
			                y = df_comunidades[df_comunidades['Comunidad'] == i]['Muertes'],
			                mode = "markers+lines",
			                name = i
			                )for i in values


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Muertes por Coronavirus por comunidades",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'}

			            )
			        }
			    )
		    ],
		    lg=12,
		),
		dbc.Col(
		    [
		    	dcc.Graph(

			        id = 'porcentaje_afectado',
			        figure = {
			            'data' : [
			                go.Scatter(

			                x = df_comunidades[df_comunidades['Comunidad'] == i]['Date'],
			                y = df_comunidades[df_comunidades['Comunidad'] == i]['porcentaje_infeccion'],
			                mode = "markers+lines",
			                name = i
			                )for i in values


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Porcentaje de población afectada por comunidad",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'}

			            )
			        }
			    )
		    ],
		),
		dbc.Col(
		    [
		    	dcc.Graph(
			        id = 'mapa_comunidades',
			        figure = {
			            'data' : [
			            	go.Scattergeo(
			            		lon = df_comunidades['Longitud'],
        						lat = df_comunidades['Latitud'],
        						text = df_comunidades['Comunidad'],
        						mode = 'markers',
        						marker = dict(
						            size = 15,
						            opacity = 0.8,
						            reversescale = True,
						            autocolorscale = False,
						            line = dict(
						                width=1,
						                color='rgba(102, 102, 102)'
						            ),
						            colorscale = scl,
						            cmin = 0,
						            color = df_comunidades['porcentaje_infeccion'],
						            cmax = df_comunidades['porcentaje_infeccion'].max(),
						            colorbar=dict(
						                title="Porcentaje de infección por comunidades"
						            )
						        )
			            	)
			               
			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
						    title = 'Porcentaje de infección por comunidades',
						    geo = dict(
						        scope = 'europe',
						        showland = True,
						        landcolor = "rgb(250, 250, 250)"
						    )
			            )
			        }
			    )
		    ],
		    lg=12,
		),
		            
	])

	return comunidades


def comunidades_layout(filter=False,values=[]):
	print("Nueva Petición")
	df_poblacion = pd.read_csv('poblacion.csv')

	url="https://s3-eu-west-1.amazonaws.com/images.webbuildeer.com/coronavirus.csv"
	s=requests.get(url).content
	df_comunidades=pd.read_csv(io.StringIO(s.decode('utf-8')))

	new = df_comunidades['Date'].str.split(' ', n = 1, expand = True)
	df_comunidades['Day'] = new[0]
	df_comunidades['Hour'] = new[1]
	df_comunidades['Comunidad2'] = df_comunidades['Comunidad']
	df_comunidades = df_comunidades.groupby(['Day','Comunidad'], as_index=False).max()

	df_comunidades = pd.merge(left=df_comunidades, right=df_poblacion, left_on='Comunidad', right_on='Comunidad')
	df_comunidades['porcentaje_infeccion'] = (df_comunidades['Casos'] / df_comunidades['Poblacion']) * 100

	if not filter:
		values = df_comunidades.Comunidad.unique()	

	global DF_COMUNIDADES 
	DF_COMUNIDADES = df_comunidades

	content = comunidades_content(df_comunidades,values)

	comunidades = html.Div([
		html.Div([
			dcc.Dropdown(
		        id='id-dropdown',
		        options=[{'label': i, 'value': i} for i in df_comunidades.Comunidad.unique()],
		        value= values,
		        multi=True,
		    )],
		    className="m-3"
	    ),
	    html.Div(
    		[content],
    		id="comunidades"
		)
    ])

	return comunidades


def internacional_content(df_world, values):

	df_world['date'] = pd.to_datetime(df_world.date)
	df_world = df_world.sort_values(['location', 'date'])

	df_world_total = df_world[df_world['location'] == 'World']
	df_world = df_world[df_world['location'] != 'World']

	total = df_world[df_world['date'] == df_world['date'].max()].sum()

	internacional = dbc.Row([
		dbc.Col(
		    [
				html.H1([dbc.Badge(str(total['total_cases']) + " Casos", className="ml-1 bg-warning")]),
			],
		    lg=6,
		    className="mt-3"
		),
		dbc.Col(
		    [
				html.H1([dbc.Badge(str(total['total_deaths']) + " Muertes", className="ml-1 bg-danger")]),
			],
		    lg=6,
		    className="mt-3"
		),	
		dbc.Col(
		    [
		    	dcc.Graph(
			        id = 'Total',
			        figure = {
			            'data' : [
			                go.Scatter(

			                x = df_world_total['date'],
			                y = df_world_total[column],
			                mode = "markers+lines",
			                name = column
			                )for column in ['total_deaths', 'total_cases']


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Casos de coronavirus en el mundo",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'}

			            )
			        }
			    )
		    ],
		    lg=12
		),	
		dbc.Col(
		    [
		    	dcc.Graph(
			        id = 'Paises',
			        figure = {
			            'data' : [
			                go.Scatter(

			                x = df_world[df_world['location'] == i]['date'],
			                y = df_world[df_world['location'] == i]['total_cases'],
			                mode = "markers+lines",
			                name = i
			                )for i in values


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Casos de coronavirus distribuidos por paises",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'}

			            )
			        }
			    )
		    ],
		    lg=12
		),
		dbc.Col(
		    [
		    	dcc.Graph(
			        id = 'Nuevos casos Total',
			        figure = {
			            'data' : [
			                go.Scatter(

			                x = df_world_total['date'],
			                y = df_world_total[column],
			                mode = "markers+lines",
			                name = column
			                )for column in ['new_deaths', 'new_cases']


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Nuevos casos de coronavirus en el mundo",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'}

			            )
			        }
			    )
		    ],
		    lg=12
		),	
		dbc.Col(
		    [
		    	dcc.Graph(
			        id = 'Nuevos casos Paises',
			        figure = {
			            'data' : [
			                go.Scatter(

			                x = df_world[df_world['location'] == i]['date'],
			                y = df_world[df_world['location'] == i]['new_cases'],
			                mode = "markers+lines",
			                name = i
			                )for i in values


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Nuevos casos de coronavirus distribuidos por paises",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'}

			            )
			        }
			    )
		    ],
		    lg=12
		),		

	])

	return internacional

def internacional_layout():
	url = 'https://s3-eu-west-1.amazonaws.com/images.webbuildeer.com/coronavirus-world.csv'
	s=requests.get(url).content
	df_world=pd.read_csv(io.StringIO(s.decode('utf-8')))
	columns = df_world.columns.tolist()

	global DF_WORLD
	DF_WORLD = df_world

	values = ['Spain', 'China', 'United States', 'Italy', 'France', 'Germany', 'United Kingdom', 'Iran']

	content = internacional_content(df_world,values)

	internacional = html.Div([
		html.Div([
			dcc.Dropdown(
		        id='internacional-dropdown',
		        options=[{'label': i, 'value': i} for i in df_world.location.unique()],
		        value= values,
		        multi=True,
		    )],
		    className="m-3"
	    ),
	    html.Div(
    		[content],
    		id="internacional"
		)
    ])

	return internacional


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

app.layout = html.Div(tabs)
app.config.suppress_callback_exceptions = True

@app.callback(Output("content", "children"), [Input("tabs", "active_tab")])
def switch_tab(at):
    if at == "espana":
        return espana_layout()
    elif at == "comunidades":
    	return comunidades_layout()
    elif at == "internacional":
        return internacional_layout()

@app.callback(
dash.dependencies.Output('comunidades', 'children'),
[dash.dependencies.Input('id-dropdown', 'value')])
def update_graph(values):
	return comunidades_content(DF_COMUNIDADES, values)


@app.callback(
dash.dependencies.Output('internacional', 'children'),
[dash.dependencies.Input('internacional-dropdown', 'value')])
def update_graph(values):
	print(values)
	return internacional_content(DF_WORLD, values)

if __name__ == '__main__':
    app.run_server()