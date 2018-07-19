
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import flask
from flask_cors import CORS

import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.plotly as py
import plotly.figure_factory as ff
from textwrap import dedent
import us

print(dcc.__version__)

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

#### INITIAL SET UP ####

#Set up colorscale
DEFAULT_COLORSCALE = ['#09091e','#ff5a1d','#ff6f39','#ff9366',
'#ffbfa2','#ffcdb7','#ffe8de','#fff1ec','#dad9e6','#cccbe3','#b9b5d5',
'#8279ad','#5d5492','#4a4185','#363178','#20206b']

DEFAULT_COLORSCALE = DEFAULT_COLORSCALE[::-1]

e1 = df_sample['HPSA Score'].min()
e2 = df_sample['HPSA Score'].max()
endpts = list(np.linspace(e1, e2, len(DEFAULT_COLORSCALE) - 3))

colors = {
    'background': '#FFFFFF',  
    'background2': '#FFFFFF',# white
    'text': '#3f3f3f' # charcoal
    }
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

#### MAIN DATASETS ####
df = pd.read_csv('https://raw.githubusercontent.com/akinnischtzke/countymap-app/master/dashdata.csv',encoding = "ISO-8859-1")
df2 = pd.read_csv('https://raw.githubusercontent.com/akinnischtzke/countymap-app/master/dashdata2.csv',encoding = "ISO-8859-1")
df_lime = pd.read_csv('https://raw.githubusercontent.com/akinnischtzke/countymap-app/master/lime_dataset_b.csv',encoding = "ISO-8859-1")

# GENERATE STATE OPTIONS LIST #
states_abbr = df.drop_duplicates(subset=['state_id'],keep='first')['state_id'].tolist()
state_list = [str(us.states.lookup(x)) for x in states_abbr]
state_options=[{'label': 'United States','value': 'all'}]
for index in range(len(state_list)-2):    
    state_options.append({'label': state_list[index],'value': states_abbr[index]})

# Remove Alaska and Hawaii from the full US map, for visualization purposes
df_sample = df.loc[df['state_id'] != 'AK']
df_sample = df_sample.loc[df_sample['state_id'] != 'HI']

# Initial county map of full US (minus AK and HI)
fig_map = ff.create_choropleth(fips=df_sample['county_fips'].tolist(), 
    values=df_sample['HPSA Score'].tolist(), #scope='usa',
    binning_endpoints=endpts,colorscale=DEFAULT_COLORSCALE,
    county_outline={'color': 'rgb(255,255,255)', 'width': 0.5}, 
    round_legend_values=True,legend_title='HPSA score', 
    title='HPSA Score by county (larger values -> greater shortage)'
    )

#Update the figure layout from defaults
w = 700 
ar = False
xr = [-125.0, -55.0]  # Initial x-axis range
yr = [24.93103448275862, 49.06896551724138] # Initial y-axis range

layout_update = dict(layout=dict(
      legend_title='HPSA shortage',
      height=w*0.5,
      width=w,
      autosize=False,
      xaxis=dict(autorange=ar,
        range=xr,
        showgrid=False,
        zeroline=False,
        showline=False,
        autotick=True,
        ticks='',
        showticklabels=False),
      yaxis=dict(autorange=ar,
        range=yr,
        showgrid=False,
        zeroline=False,
        showline=False,
        autotick=True,
        ticks='',
        showticklabels=False),
      paper_bgcolor=colors['background'],
      plot_bgcolor=colors['background'],
      margin=dict(left=0, right=0,bottom=0, t=0),
      padding=0,
      #scope=['usa'],
      ))

fig_map.update(layout_update)

# Initial set up for LIME graph
fig_lime = go.Figure(
  data=[go.Bar(
    x=[],
    y=[],
    )], 
  layout=go.Layout(
    xaxis=dict(
        showgrid=False,
        showline=False,
        showticklabels=False,#True,
        zeroline=False,
        domain=[0.15, 1]
    ),
    yaxis=dict(
        showgrid=False,
        showline=False,
        showticklabels=False,#True,
        zeroline=True,
        domain=[0.15, 1]
    ),
    paper_bgcolor=colors['background2'],
    plot_bgcolor=colors['background2'],
    margin=dict(l=120, r=100,b=0, t=30),
    ))

# Making graph for top or bottom county lists
df_sorted = df2.sort_values('HPSA Prediction',ascending=False)
df_sorted2 = df2.sort_values('HPSA Prediction',ascending=True)
df_sorted.reset_index(drop=True, inplace=True)
df_sorted2.reset_index(drop=True, inplace=True)

x_data1 = df_sorted.iloc[0:11]['HPSA Prediction']
y_data1 = df_sorted.iloc[0:11]['countystate']
x_data2 = df_sorted2.iloc[0:11]['HPSA Prediction']
y_data2 = df_sorted2.iloc[0:11]['countystate']

data1 = [{"x": x_data1, 
          "y": y_data1, 
          "marker": {"color": "#ff7a4a", "size": 12}, 
          "mode": "markers", 
          "name": "Women", 
          "type": "scatter"       
}]
data2 = [{"x": x_data2, 
          "y": y_data2, 
          "marker": {"color": "#4A4185", "size": 12}, 
          "mode": "markers", 
          "name": "Women", 
          "type": "scatter"       
}]

layout1 = {"title": "10 counties with greatest shortage", 
          "xaxis": {"title": "HPSA prediction","range": [5,20]}, 
          "yaxis": {"autorange": "reversed"},
          "margin": {"l": 220,"r": 180,"t": 60,}
          }
layout2 = {"title": "10 counties with least shortage", 
          "xaxis": {"title": "HPSA prediction","range": [5,20]}, 
          "yaxis": {"autorange": "reversed"},
          "margin": {"l": 220,"r": 180,"t": 60,}
          }

fig_chart = go.Figure(data=data1, layout=layout1)


#base_url = 'https://raw.githubusercontent.com/akinnischtzke/mapbox-counties/master/hpsa-data_pred'
#geo_sources = [base_url + str(r) + '.json' for r in range(25)]


############ APP LAYOUT ##################
app.layout = html.Div([

  html.H1(children='Doctors Within Borders',
    style={
    'textAlign': 'center',
    'color': colors['text'],
    'backgroundColor':colors['background'],
    }),


  html.H6(children='Where should new doctors set up a practice?', style={
    'textAlign': 'center',
    'color': colors['text'], 
    'backgroundColor':colors['background'],
    }),

  dcc.Tabs(vertical=False,id="tabs", children=[

    # Tab 1
    dcc.Tab(label='About', children=[
      html.Div([
      html.Div([
        dcc.Markdown(dedent('''
        **About me**

        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Hi! My name is Amanda Kinnischtzke, and I have recently become a data scientist after spending 
        the last ten years in academia as an experimental neuroscientist. I have a PhD in Neuroscience 
        from the University of Pittsburgh, and spent the last 4 years as a postdoctoral research fellow 
        at Columbia University in New York City. At Columbia, I studied somatosensory processing – 
        understanding how the brain takes in touch information, makes sense of it, and then makes a 
        decision about how to respond. &nbsp;&nbsp;

        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This project was developed during my first few weeks as a Fellow at Insight Data Science 
        in New York. I hope you enjoy!
        '''
        )
        ),
        ],className='eight columns', style = {'marginLeft': 60,'marginTop': 60,'marginRight': 60,},
        ),
      html.Div([
        dcc.Markdown(dedent('''
        **About the project**

        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; If the name, “Doctors Within Borders” seems familiar at all, it probably reminds you of “Doctors Without Borders”, an international NGO which places qualified physicians in locations where the need is greatest. This is not by accident! It is well-known that availability of quality healthcare *within* the United States fluctuates wildly depending on location. One of the reasons is shortages of primary care physicians. 

        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; My goal with this website is to identify the areas within the United States of America that currently have the greatest primary care shortages, with the hope that young physicians can use this information to decide where to setup a new practice and state administrators can quickly identify problem areas in their states. 

        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; I am focusing on The Bureau of Health Workforce process, which has a designation known as a Health Professional Shortage Area (HPSA) score. This score measures the degree of primary care shortage for individual areas, with reporting areas as small as single counties. However, the current process for scoring a region is done manually, resulting in a bottleneck for identifying the areas around the country where shortages exist. Currently, only about 12 percent of all US counties have an up-to-date score. 

        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; I developed this website to serve as a platform for modeling the HPSA score, which results in immediate and up-to-date scoring of individual counties. I am using data sources that are related to those used in the HPSA designation and are publically available for all counties in the United States (e.g. US Census, CDC, and Medicare datasets). The model scoring predictions follow the current HPSA scoring convention, which varies between 0 and 25, with higher values reflecting higher need. 

        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; By developing a predictive model for HPSA scores, we can immediately 1) identify areas of greatest need around the country, 2) automatically update scores as regions change over time, and 3) pinpoint specific aspects of healthcare that are causing an area to have greater than average primary care shortage.

        '''
        )),
        ],className='eight columns', style = {'marginLeft': 60,'marginTop': 60,'marginRight': 60,},
        ),
      
        ],className='row'
        )
      ]),

    # Tab 2
    dcc.Tab(label='County lists', children=[

      html.Div([
        dcc.RadioItems(
          id='shortage-type',
          options=[{'label': i, 'value': i} for i in ['Greatest shortage', 'Least shortage']],
          value='Greatest shortage',
          labelStyle={'display': 'inline-block'}
          ),
        dcc.Graph(id='top-counties',figure=fig_chart),
        ], style = {'marginLeft': 60,'marginRight': 60},
        ),
      ]),

    # Tab 3
    dcc.Tab(label='Single county exploration', children=[

      html.Div([
        html.Div([
            html.H3(' '), #Column 1
            html.P('Choose a state:'),
            dcc.Dropdown(
              id='state_pick',
              options=state_options,
              multi=False,
              value='all',
              ),
            html.H6('Predicted HPSA scores *',
              style={
              'textAlign': 'center',
              'color': colors['text'],
              'backgroundColor':colors['background'],
              }),
            
            dcc.Graph(id='ff-map',figure=fig_map,
              config={'displayModeBar': False},
              ),
            ], className="seven columns",style = {'marginLeft': 0},
            ),

        html.Div([
          html.Div([
            html.H3(' '), #Column 2
            dcc.Markdown(''' ''',id='county-name'),
            dcc.Markdown(''' ''',id='county-pop'),
            dcc.Markdown(''' ''',id='county-PCperc'),
            #html.P(' '),
            #html.P(' '),
            ],style={'textAlign': 'center',
                   'color': colors['text'], 
                   'backgroundColor': colors['background2'],
                   'marginTop': 0,
                   'marginTop': 0,
                   'marginLeft': 120,
                   'marginRight': 0, 
                   'width':'79%',
                   'vertical-align': 'middle'},
            ),
            
            html.Div([
              dcc.Graph(id='lime-chart',figure=fig_lime,
                config={'displayModeBar': False},
                ),
              ], className="three columns", 
              style={'marginTop': 30,
                     'marginLeft': 70,
                     'vertical-align': 'middle',
                     },
              ),
            ], className="three columns", 
            style={'textAlign': 'center',
                   'color': colors['text'], 
                   'backgroundColor': colors['background2'],
                   'marginTop': 70,
                   'marginLeft': 0,
                   'marginRight': 0, 
                   'width':'25%',
                   'vertical-align': 'middle'}
            ),
        ], className="row"),
html.P('* Low scores (min of 0) indicate little or no primary care shortage; high scores (max of 25) indicate severe primary care shortage'),
]),
]),
])


#########################################

# Update top vs bottom county lists (tab 2)
@app.callback(
    dash.dependencies.Output('top-counties', 'figure'),
    [dash.dependencies.Input('shortage-type', 'value')])
def update_graph(shortage_type):
  if shortage_type == 'Greatest shortage':
      fig_chart = go.Figure(data=data1, layout=layout1)
  else:
      fig_chart = go.Figure(data=data2, layout=layout2)

  return fig_chart

# Update main US map, based on state selection
@app.callback(Output('ff-map', 'figure'),
  [Input('state_pick', 'value')])

def make_main_figure(state_pick):

  if state_pick == 'all': # If full US map selected
    
    # Remove Alaska and Hawaii from the full US map, messes up graph
    df_sample = df.loc[df['state_id'] != 'AK']
    df_sample = df_sample.loc[df_sample['state_id'] != 'HI']

    #Update the figure layout from defaults
    w = 700 #600
    #h = 700#500
    ar = False
    xr = [-125.0, -55.0]  # Initial x-axis range
    yr = [24.93103448275862, 49.06896551724138] # Initial y-axis range

    layout_update = dict(layout=dict(
      legend_title='HPSA shortage',
      height=w*0.5,
      width=w,
      autosize=False,
      xaxis=dict(autorange=ar,
        range=xr,
        showgrid=False,
        zeroline=False,
        showline=False,
        autotick=True,
        ticks='',
        showticklabels=False),
      yaxis=dict(autorange=ar,
        range=yr,
        showgrid=False,
        zeroline=False,
        showline=False,
        autotick=True,
        ticks='',
        showticklabels=False),
      paper_bgcolor=colors['background'],
      plot_bgcolor=colors['background'],
      margin=dict(left=0, right=0,bottom=0, t=0),
      padding=0,
      hoverdistance=2,
          #scope=['usa'],
          ))
  
  else: # for any individual state selection
    df_sample = df.loc[df['state_id'] == state_pick]
    w = 800 #600
    h = 700#500
    ar = True

    layout_update = dict(layout=dict(
      height=h,
      #width=w,
      autosize=ar,
      xaxis=dict(autorange=True,
        #range=xr,
        showgrid=False,
        zeroline=False,
        showline=False,
        autotick=True,
        ticks='',
        showticklabels=False),
      yaxis=dict(autorange=True,
        #range=yr,
        showgrid=False,
        zeroline=False,
        showline=False,
        autotick=True,
        ticks='',
        showticklabels=False),
      paper_bgcolor=colors['background'],
      plot_bgcolor=colors['background'],
      margin=dict(left=00, right=30,bottom=30, t=30),
      hovermode='closest',
      hoverdistance=10,
      #scope=['usa'],
      ))


  fig_map = ff.create_choropleth(fips=df_sample['county_fips'].tolist(), 
    values=df_sample['HPSA Score'].tolist(), scope=[state_pick],
    binning_endpoints=endpts,colorscale=DEFAULT_COLORSCALE,
    county_outline={'color': 'rgb(255,255,255)', 'width': 0.5}, 
    round_legend_values=True,title='HPSA score by County') 
        #title='HPSA Score by county')  
  
  fig_map.update(layout_update)

  return fig_map

# Update text in right column based on hoverData from map
@app.callback(Output('county-name', 'children'),
      [Input('ff-map', 'hoverData')])
def update_text(hoverData):

      text = hoverData['points'][0]['text']
      start = text.find('FIPS: ') + 6
      end = text.find('<',start)
      fips = int(text[start:end])
      s = df[df['county_fips'] == fips]
      r = s.iloc[0]['countynames']
      r = r.rstrip(',')
      r2 = "{:,}".format(s.iloc[0]['POP_ESTIMATE_2016']).replace(".0"," ")
      r3 = "{}".format(s.iloc[0]['HPSA Score']).replace(".0"," ")
      
      return dedent('''
        
        **County:** {}
        
        **Population:** {} 
        
        **Estimated HPSA Score:** {} 

        '''.format(r,r2,r3)) 

# Update LIME graph based on hoverData from map
@app.callback(Output('lime-chart', 'figure'),
  [Input('ff-map', 'hoverData')])

def make_lime_chart(hoverData):
  text = hoverData['points'][0]['text']
  start = text.find('FIPS: ') + 6
  end = text.find('<',start)
  fips = float(text[start:end])
  
  #s = df[df['county_fips'] == fips]
  d = df_lime.loc[df_lime['county_fips'] == fips]
  print(d.shape)
  
  data = [go.Bar(
    x=d['value'],
    y=d['dash text'], 
    orientation = 'h',
    text=d['value'],
    marker = dict(
      color = d['bar color'],
      opacity=1,
      line = dict(
        color = d['bar color'],
        width = 1),
      ),
    )]

  layout = go.Layout(
    height=300,
    width=400,
    autosize=True,
    title='Features driving prediction',
    xaxis=dict(
      title='Amount',
      showgrid=False,
      showline=False,
      showticklabels=True,
      zeroline=True,
      domain=[0.15, 1]
      ),
    yaxis=dict(
      showgrid=False,
      showline=False,
      showticklabels=True,
      zeroline=False,
      ),
    barmode='stack',
    paper_bgcolor=colors['background2'], #'#09091e',
    plot_bgcolor=colors['background2'],
    margin=dict(
      l=180,#500,
      r=0,#00,
      t=40,#100,
      b=80,#00
      ),
    showlegend=False,
    hovermode=False,
    )

  fig_lime = go.Figure(data=data, layout=layout)

  return fig_lime



app.css.append_css({
    'external_url': 'https://codepen.io/amandakinnischtzke/pen/zaeooO.css'
})

#if __name__ == '__main__':
#  app.run_server(debug=True)

if __name__ == '__main__':
     #change host from the default to '0.0.0.0' to make it publicly available
     app.server.run(port=8000, host='0.0.0.0')

