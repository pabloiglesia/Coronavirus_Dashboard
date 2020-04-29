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
# df_internacional = df_internacional.groupby(['FECHA', 'Country/Region'], as_index=False).max()


TEMPLATE = "plotly_dark"

DF_ESPANA = None
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
		                dbc.Tab(label="General España", tab_id="espana"),
		                dbc.Tab(label="Comparación de Comunidades", tab_id="comunidades"),
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

def get_comunidades():
	url = 'https://covid19.isciii.es/resources/serie_historica_acumulados.csv'
	# url = 'https://s3-eu-west-1.amazonaws.com/images.webbuildeer.com/coronavirus.csv'
	df_poblacion = pd.read_csv('poblacion.csv')
	df_comunidades = pd.read_csv(url, encoding='latin1')
	df_comunidades = df_comunidades.fillna(value=0)
	df_comunidades = pd.merge(left=df_comunidades, right=df_poblacion, left_on='CCAA', right_on='CCAA')
	df_comunidades['FECHA'] = pd.to_datetime(df_comunidades.FECHA, format='%d/%m/%Y')
	df_comunidades['Casos acumulados (PCR)'] = max(df_comunidades['Casos'], df_comunidades['PCR+'])
	df_comunidades['Test Rápdos'] = df_comunidades['TestAc+']
	df_comunidades = df_comunidades.sort_values(by=['Comunidad', 'FECHA'], ascending=True)


	df_comunidades['nuevos_infectados'] = df_comunidades['Casos acumulados (PCR)'].diff()
	df_comunidades['nuevas_muertes'] = df_comunidades['Fallecidos'].diff()
	df_comunidades['nuevas_altas'] = df_comunidades['Recuperados'].diff()
	df_comunidades['nuevas_hospitalizados'] = df_comunidades['Hospitalizados'].diff()
	df_comunidades['nuevas_UCI'] = df_comunidades['UCI'].diff()
	df_comunidades['nuevos_PCR+'] = df_comunidades['PCR+'].diff()
	df_comunidades['nuevas_TestAc'] = df_comunidades['Test Rápdos'].diff()
	df_comunidades = df_comunidades[df_comunidades['FECHA'] != df_comunidades['FECHA'].min()]

	df_comunidades['porcentaje_infeccion'] = (df_comunidades['Casos acumulados (PCR)'] / df_comunidades['Poblacion']) * 100
	df_comunidades['tasa_contagio'] = df_comunidades['nuevos_infectados'] / (df_comunidades['Casos acumulados (PCR)'] - df_comunidades['nuevos_infectados'])
	df_comunidades['Casos activos'] = df_comunidades['Casos acumulados (PCR)'] - df_comunidades['Fallecidos'] - df_comunidades['Recuperados']
	df_comunidades['infectados_dia'] = df_comunidades['nuevos_infectados'] - df_comunidades['nuevas_muertes'] - df_comunidades['nuevas_altas']

	return df_comunidades


def kpis(df, filter="No filtrar"):

	if filter != "No filtrar":
		df = df[df['Comunidad'] == filter]
		poblacion = df['Poblacion'].max()
	else:
		df = df.groupby('FECHA', as_index=False).sum()
		poblacion = 47000000

	kpis = dbc.Row([
		dbc.Col(
		    [
				html.H1([dbc.Badge(str(int(df['Casos acumulados (PCR)'].max())) + " Casos", className="ml-1 bg-warning")]),
			],
		    lg=4,
		    className="mt-3 mt-3"
		),
		dbc.Col(
		    [
				html.H1([dbc.Badge(str(int(df['Fallecidos'].max())) + " Muertes", className="ml-1 bg-danger")]),
			],
		    lg=4,
		    className="mt-3 mt-3"
		),		
		dbc.Col(
		    [
				html.H1([dbc.Badge(str(int(df['Recuperados'].max())) + " Altas", className="ml-1 bg-success")]),
		    ],
		    lg=4,
		    className="mt-3 mt-3"
		),
		dbc.Col(
		    [
				html.H1([dbc.Badge(str(int(df['Hospitalizados'].max())) + " Hospital", className="ml-1 bg-info")]),
			],
		    lg=4,
		    className="mt-3 mt-3"
		),
		dbc.Col(
		    [
				html.H1([dbc.Badge(str(int(df['UCI'].max())) + " En UCI", className="ml-1 bg-info")]),
			],
		    lg=4,
		    className="mt-3 mt-3"
		),		
		dbc.Col(
		    [
				html.H1([dbc.Badge(str(round((int(df['Casos acumulados (PCR)'].max())/poblacion)*100, 2)) + "% Población", className="ml-1 bg-info")]),
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
			                x = df['FECHA'],
			                y = df[column],
			                mode = "markers+lines",
			                name = column
			                )for column in ['Casos acumulados (PCR)', 'Fallecidos', 'Recuperados']


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Casos de coronavirus",
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
			                x = df['FECHA'],
			                y = df[column],
			                mode = "markers+lines",
			                name = column
			                )for column in ['Casos activos', 'Casos acumulados (PCR)', 'Hospitalizados', 'Test Rápdos']


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Casos activos",
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
			        id = 'Total UCI',
			        figure = {
			            'data' : [
			                go.Scatter(
			                x = df['FECHA'],
			                y = df['UCI'],
			                mode = "markers+lines"
							)


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Total de personas en la UCI",
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

			                x = df['FECHA'],
			                y = df['nuevos_infectados'],
			                name = "Nuevos infectados"
			                )


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Contagiados por día",
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
			        id = 'infectados_dia',
			        figure = {
			            'data' : [
			                go.Bar(

			                x = df['FECHA'],
			                y = df['infectados_dia'],
			                name = "Portadores activos por día"
			                )


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Portadores activos por día",
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
			        id = 'nuevas_murtes',
			        figure = {
			            'data' : [
			                go.Bar(

			                x = df['FECHA'],
			                y = df['nuevas_muertes'],
			                name = "Nuevas Muertes",
			                marker = dict(
			                	color='red'
			                	)
			                )


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Muertes por día",
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

			                x = df['FECHA'],
			                y = df['nuevas_altas'],
			                name = "Nuevas Altas",
			                marker = dict(
			                	color='lightgreen'
			                	)
			                )
			             ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Altas por día",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'},
			           

			            )
			        }
			    )
		    ],
		    lg=6,
		),
				dbc.Col(
		    [
		    	dcc.Graph(
			        id = 'nuevas_UCI',
			        figure = {
			            'data' : [
			                go.Bar(

			                x = df['FECHA'],
			                y = df['nuevas_UCI'],
			                name = "Variación de personas en la UCI",
			                marker = dict(
			                	color='violet'
			                	)
			                )


			            ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Variación de personas en la UCI",
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
			        id = 'nuevos_hospitalizados',
			        figure = {
			            'data' : [
			                go.Bar(

			                x = df['FECHA'],
			                y = df['nuevas_hospitalizados'],
			                name = "Nuevas hospitalizaciones",
			                marker = dict(
			                	color='violet'
			                	)
			                )
			             ],
			            'layout' : go.Layout(
			            	template = TEMPLATE,
			                title = "Hospitalizados por día",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'},
			           

			            )
			        }
			    )
		    ],
		    lg=6,
		),
	])

	return kpis


def espana_layout():
	df = get_comunidades()

	global DF_ESPANA 
	DF_ESPANA = df

	filter = "No filtrar"

	content = kpis(df, filter = filter)

	espana = dbc.Container(
	[
		html.H5('Filtrar por comunidad autónoma'),

		html.Div([
			dcc.Dropdown(
		        id='espana-dropdown',
		        options=[{'label': i, 'value': i} for i in np.insert(df.Comunidad.unique(), 0, filter) ],
		        value= filter,
		        multi=False,
		    )],
		    className="m-3"
	    ),
	    html.Div(
    		[content],
    		id="espana-div"
		)
	],
	className="mt-4 text-center",
	)

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

			                x = df_comunidades[df_comunidades['Comunidad'] == i]['FECHA'],
			                y = df_comunidades[df_comunidades['Comunidad'] == i]['Casos acumulados (PCR)'],
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

			                x = df_comunidades[df_comunidades['Comunidad'] == i]['FECHA'],
			                y = df_comunidades[df_comunidades['Comunidad'] == i]['Fallecidos'],
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

			                x = df_comunidades[df_comunidades['Comunidad'] == i]['FECHA'],
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
	df_comunidades = get_comunidades()

	if not filter:
		values = df_comunidades.Comunidad.unique()	

	global DF_ESPANA 
	DF_ESPANA = df_comunidades

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
	url = 'https://covid.ourworldindata.org/data/ecdc/full_data.csv'
	# url = 'https://s3-eu-west-1.amazonaws.com/images.webbuildeer.com/coronavirus-world.csv'
	s=requests.get(url).content
	df_world=pd.read_csv(io.StringIO(s.decode('utf-8')))
	columns = df_world.columns.tolist()

	print(columns)
	print(df_world)

	df_world['date'] = pd.to_datetime(df_world.date)

	global DF_WORLD
	DF_WORLD = df_world

	values = df_world[df_world['date'] == df_world['date'].max()].sort_values('total_cases', ascending=False)['location'].head(11)[1:]

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
	return comunidades_content(DF_ESPANA, values)


@app.callback(
dash.dependencies.Output('internacional', 'children'),
[dash.dependencies.Input('internacional-dropdown', 'value')])
def update_graph(values):
	print(values)
	return internacional_content(DF_WORLD, values)


@app.callback(
dash.dependencies.Output('espana-div', 'children'),
[dash.dependencies.Input('espana-dropdown', 'value')])
def update_graph(value):
	print(value)
	return kpis(DF_ESPANA, value)


if __name__ == '__main__':
    app.run_server()