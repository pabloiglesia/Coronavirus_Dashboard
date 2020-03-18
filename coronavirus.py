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

tabs = dbc.Container(
	[
		html.H1('Evolución Covid-19'),
		html.Div([
	        html.P('En este Dashboard se muestra la evolución del coronavirus en España en tiempo real. Los datos se actualizan cada media hora y la fuente oficial es Ministerio de Sanidad y consejerías autonómicas.')
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
	df_total['tasa_contagio'] = df_total['nuevos_infectados'] / (df_total['Casos'] - df_total['nuevos_infectados'])

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
			                title = "Tasa de contagio en España",
			                xaxis = {'title': 'Fecha'},
			                yaxis = {'title': 'Personas'}

			            )
			        }
			    )
		    ],
		    lg=12,
		),
	

	])

	return espana

def comunidades_layout():
	df_poblacion = pd.read_csv('poblacion.csv')

	url="https://s3-eu-west-1.amazonaws.com/images.webbuildeer.com/coronavirus.csv"
	s=requests.get(url).content
	df_comunidades=pd.read_csv(io.StringIO(s.decode('utf-8')))

	new = df_comunidades['Date'].str.split(' ', n = 1, expand = True)
	df_comunidades['Day'] = new[0]
	df_comunidades['Hour'] = new[1]
	df_comunidades['Comunidad2'] = df_comunidades['Comunidad']
	df_comunidades = df_comunidades.groupby(['Day','Comunidad2']).max()

	df_comunidades = pd.merge(left=df_comunidades, right=df_poblacion, left_on='Comunidad', right_on='Comunidad')
	df_comunidades['porcentaje_infeccion'] = (df_comunidades['Casos'] / df_comunidades['Poblacion']) * 100

	df = px.data.gapminder().query("year == 2007")

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
			                )for i in df_comunidades.Comunidad.unique()


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
			                )for i in df_comunidades.Comunidad.unique()


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
			                )for i in df_comunidades.Comunidad.unique()


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
		#                 dbc.Col(
		#                     [
		#                     	dcc.Graph(
		# 
		# 					        id = 'Casos_Internacionales',
		# 					        figure = {
		# 					            'data' : [
		# 					                go.Scatter(
		# 
		# 					                x = df_internacional[df_internacional['Country'] == i]['Date'],
		# 					                y = df_internacional[df_internacional['Country'] == i]['Cases'],
		# 					                mode = "markers+lines",
		# 					                name = i
		# 					                )for i in df_internacional.Country.unique()
		# 
		# 
		# 					            ],
		# 					            'layout' : go.Layout(
		# 					            	template = TEMPLATE,
		# 					                title = "Casos de Coronavirus por Países",
		# 					                xaxis = {'title': 'Fecha'},
		# 					                yaxis = {'title': 'Personas'}
		# 
		# 					            )
		# 					        }
		# 					    )
		#                     ],
		#                     xs=12
		#                 ),
		            
	])

	return comunidades

def internacional_layout():
	url = 'https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_19-covid-Confirmed.csv&filename=time_series_2019-ncov-Confirmed.csv'
	s=requests.get(url).content
	df_world=pd.read_csv(io.StringIO(s.decode('utf-8')))
	columns = df_world.columns.tolist()
	df_world = df_world.melt(id_vars=columns[:4], 
	        var_name="Date", 
	        value_name="Cases").groupby(['Date', 'Country/Region'], as_index=False).sum()

	df_world['Country'] = df_world['Country/Region']
	df_world['Date'] = pd.to_datetime(df_world.Date)
	df_world = df_world.sort_values(['Country', 'Date'])



	url = 'https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_19-covid-Deaths.csv&filename=time_series_2019-ncov-Deaths.csv'
	s=requests.get(url).content
	df_world_deaths=pd.read_csv(io.StringIO(s.decode('utf-8')))
	columns = df_world_deaths.columns.tolist()
	df_world_deaths = df_world_deaths.melt(id_vars=columns[:4], 
	        var_name="Date", 
	        value_name="Cases").groupby(['Date', 'Country/Region'], as_index=False).sum()

	df_world_deaths['Country'] = df_world_deaths['Country/Region']
	df_world_deaths['Date'] = pd.to_datetime(df_world_deaths.Date)
	df_world_deaths = df_world_deaths.sort_values(['Country', 'Date'])



	url = 'https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_19-covid-Recovered.csv&filename=time_series_2019-ncov-Recovered.csv'
	s=requests.get(url).content
	df_world_recoveries=pd.read_csv(io.StringIO(s.decode('utf-8')))
	df_world_recoveries=pd.read_csv(io.StringIO(s.decode('utf-8')))
	columns = df_world_recoveries.columns.tolist()
	df_world_recoveries = df_world_recoveries.melt(id_vars=columns[:4], 
	        var_name="Date", 
	        value_name="Cases").groupby(['Date', 'Country/Region'], as_index=False).sum()

	df_world_recoveries['Country'] = df_world_recoveries['Country/Region']
	df_world_recoveries['Date'] = pd.to_datetime(df_world_recoveries.Date)
	df_world_recoveries = df_world_recoveries.sort_values(['Country', 'Date'])

	df_world['Country'] = df_world['Country/Region']
	df_world['Date'] = pd.to_datetime(df_world.Date)
	df_world = df_world.sort_values(['Country', 'Date'])

	df_world_sin_china = df_world[df_world['Country'] != 'China']
	df_world_sin_china = df_world_sin_china[df_world_sin_china['Date'] > '2020-02-23']

	num_contagios = df_world[df_world['Date'] == df_world['Date'].max()].sum()
	num_muertes = df_world_deaths[df_world_deaths['Date'] == df_world_deaths['Date'].max()].sum()
	num_recuperados = df_world_recoveries[df_world_recoveries['Date'] == df_world_recoveries['Date'].max()].sum()

	internacional = dbc.Row([
		dbc.Col(
		    [
				html.H1([dbc.Badge(str(num_contagios['Cases']) + " Casos", className="ml-1 bg-warning")]),
			],
		    lg=4,
		    className="mt-3 mt-3"
		),
		dbc.Col(
		    [
				html.H1([dbc.Badge(str(num_muertes['Cases']) + " Muertes", className="ml-1 bg-danger")]),
			],
		    lg=4,
		    className="mt-3 mt-3"
		),		
		dbc.Col(
		    [
				html.H1([dbc.Badge(str(num_recuperados['Cases']) + " Altas", className="ml-1 bg-success")]),
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

			                x = df_world[df_world['Country'] == i]['Date'],
			                y = df_world[df_world['Country'] == i]['Cases'],
			                mode = "markers+lines",
			                name = i
			                )for i in df_world.Country.unique()


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
			        id = 'Total',
			        figure = {
			            'data' : [
			                go.Scatter(

			                x = df_world_sin_china[df_world_sin_china['Country'] == i]['Date'],
			                y = df_world_sin_china[df_world_sin_china['Country'] == i]['Cases'],
			                mode = "markers+lines",
			                name = i
			                )for i in df_world_sin_china.Country.unique()


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

	])

	return internacional


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

app.layout = html.Div(tabs)

@app.callback(Output("content", "children"), [Input("tabs", "active_tab")])
def switch_tab(at):
    if at == "espana":
        return espana_layout()
    elif at == "comunidades":
        return comunidades_layout()
    elif at == "internacional":
        return internacional_layout()

if __name__ == '__main__':
    app.run_server()

