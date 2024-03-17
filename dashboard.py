from gc import callbacks
from msilib.schema import Component
# from optparse import Option
# from pickle import NONE
# from tkinter.ttk import Style
# from turtle import width
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output 

import state_code

app = Dash(__name__)

data = pd.read_csv("gun_violance.csv")


app.layout = html.Div(

    [
    html.H1("US Gun Violence Analysis Dashboard", style={'text-align': 'center'}),

    dcc.Dropdown(id='select_year',
                 options=[
                     {"label": "2013", "value": 2013},
                     {"label": "2014", "value": 2014},
                     {"label": "2015", "value": 2015},
                     {"label": "2016", "value": 2016},
                     {"label": "2017", "value": 2017},
                     {"label": "2018", "value": 2018}],
                 multi=False,
                 value=2013,
                 style={'width': "30%", "display": "inline-block", "grid-gap": "10px"}
                 ),

    dcc.Dropdown(id='type',
                 options=[
                     {'label':'incident','value':'incidents'},
                     {'label':'killed','value':'n_killed'}
                 ],
                 multi = False,
                 value='incidents',
                 style={'width': "30%", "display": "inline-block", "grid-gap": "10px"}
                 ),

    dcc.Dropdown(id="states",
                 options=state_code.state_options,
                 value="AL",
                 style={'width': "30%", "display": "inline-block", "grid-gap": "10px"}
                 ),

    dcc.Graph(id="map", figure={},style={'width': "50%","display":"inline-block","grid-gap": "10px"}),

    dcc.Graph(id='line', figure={},style={'width': "50%","display":"inline-block","grid-gap": "10px"}),
 
 html.Div([
    dcc.Graph(id='bar', figure={},style={'width':'50%','height': "500px","display":"inline-block","grid-gap": "10px"}),
    

    html.Div([
    dcc.Dropdown(id='age_gender',
                 options=[
                     {'label':'gender','value':'gender'},
                     {'label':'age','value':'age'}
                 ],
                 multi = False,
                 value='gender',
                 style={'width': "60%"}
                 ),
    dcc.Graph(id='pie-chart', figure={},style={'width':'100%'}),
    ],style={'width':'50%','height': "500px","display":"inline-block","grid-gap": "10px"})
    
 ],style={'width':'100%',"display":"inline-block"}),


 dcc.Dropdown(id='causes', 
              options=[],
              value=None,
              multi=False,
              style={'width':'70%'}),

dcc.Graph(id='cities')
    
])

@app.callback(
    [Output(component_id="map", component_property='figure')],
    [Input(component_id="select_year", component_property='value'),
     Input(component_id="type", component_property='value')]
)
def update_graph(selected_year, type):
    dff = data.copy()
    
    color = None
    hover_data = None
    labels = None
    if type == 'n_killed':
        color = 'n_killed'
        hover_data = 'n_killed'

        dff = dff.groupby(['state', 'state_code', 'year'])['n_killed'].sum().reset_index()
        labels = {'incident_id': 'Incident Count'}
    else:
        color = 'incident_id'
        hover_data = 'incident_id'

        dff = dff.groupby(['state', 'state_code', 'year']).count().reset_index()
        labels = {'Killed': 'killed Count'}
    
    dff = dff[dff['year'] == selected_year]

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='state_code',
        scope="usa",
        color=color,  # Change this to the column you want to display
        hover_data=['state', hover_data],
        color_continuous_scale=px.colors.sequential.YlOrRd,
        labels=labels,
        template='plotly_dark'
    )

    return [fig]

@app.callback(
    [Output(component_id='line',component_property='figure'),
     Output(component_id='bar',component_property='figure'),
     Output(component_id='pie-chart',component_property='figure'),
     Output(component_id='causes',component_property='options'),
     Output(component_id='causes',component_property='value')],

    [Input(component_id='states',component_property='value'),
     Input(component_id="select_year", component_property='value'),
     Input(component_id="type", component_property='value'),
     Input(component_id="age_gender", component_property='value')]
    )
def update_line(states,year,type,age_gender):
    dff = data.copy()
    dff = dff[['state','state_code','year','month','n_killed','cause','adults','teen','child','male','female']]
    
   
    per_month = []
    for month in range(1,13):
        if type == 'incidents':
            per_month.append(dff[(dff['state_code'] == states) & (dff['year'] == year) & (dff['month'] == month)].shape[0])
        elif type == 'n_killed':
            per_month.append(dff[(dff['state_code'] == states) & (dff['year'] == year) & (dff['month'] == month)]['n_killed'].sum())
    
    #gender and age ratio
    gender_age_count = []
    gender_or_age = []
    
    ratio = None

    if age_gender == 'gender':
        gender_age_count.append(dff[(dff['state_code'] == states) & (dff['year'] == year)]['male'].sum())
        gender_age_count.append(dff[(dff['state_code'] == states) & (dff['year'] == year)]['female'].sum())

        gender_or_age = ['male','female']
        ratio = "gender ration in gun violance incidents"
    else:
        gender_age_count.append(dff[(dff['state_code'] == states) & (dff['year'] == year)]['adults'].sum())
        gender_age_count.append(dff[(dff['state_code'] == states) & (dff['year'] == year)]['teen'].sum())
        gender_age_count.append(dff[(dff['state_code'] == states) & (dff['year'] == year)]['child'].sum())

        gender_or_age = ['adults','teen','child']
        ratio = "age categories in gun violance incidents"
    

    # causes for gun violance incidents
    
    sorted = None
    top_reason = None
    if type == 'incidents':
        dff = dff[(dff['state_code'] == states) & (dff['year'] == year)].groupby(['cause']).count().reset_index()
        dff = dff[['cause','state']]
        sorted = dff.sort_values(by='state', ascending=False)

        top_reason = sorted.head(10)
        X_LABEL = top_reason.cause.str[:30]
        Y_VALUE = top_reason.state
    else:
        data2 = data.copy()
        new_dff = data2[(data2['state_code'] == states) & (data2['year'] == year)]
        new_data = new_dff.groupby(['cause'])['n_killed'].sum().reset_index()
        sorted = new_data.sort_values(by='n_killed', ascending=False)
        
        top_reason = sorted.head(10)
        X_LABEL = top_reason.cause.str[:30]
        Y_VALUE = top_reason.n_killed
    
    

    
  
    figs = px.bar(x=X_LABEL, y= Y_VALUE, title='Top reason of gun violance',
                 color=Y_VALUE)
    
    
    pie_chart = px.pie( names=gender_or_age, values=gender_age_count, title=ratio)
    
    causes = []
    # for reason in  top_reason.cause:
    #     option = {'label': reason, 'value': reason}

    #     causes.append(option)
        

    # causes = [{'label': 'state', 'value':' code'},
    #           {'label': 'state2', 'value':' code2'}]
    new_options = [{'label': f' {i}', 'value': f'{i}'} for i in top_reason.cause]
    new_value = new_options[0]['value'] if new_options else None
    
    
    return [{'data': [
                go.Scatter(x=['1','2','3','4','5','6','7','8','9','10','11','12'], y=per_month, mode='lines', name=' Disease'),
                
            ],
            'layout': go.Layout(title='12 month data')},figs,pie_chart,new_options,new_value]


@app.callback(
    [Output(component_id='cities',component_property='figure')],
    [Input(component_id='causes',component_property='value'),
     Input(component_id='states',component_property='value'),
     Input(component_id="select_year", component_property='value')],

    
)

def city_list(causes,states,year):
    data2 = data.copy()
    new_dff = data2[(data2['state_code'] == states) & (data2['year'] == year) & (data2['cause'] == causes) ].groupby('city_or_county').count().reset_index()
    new_dff[['city_or_county','incident_id']]
    
    figs = px.bar(x=new_dff.city_or_county, y= new_dff.incident_id, title='Incidents by county',
                 color=new_dff.incident_id)
    return [figs]


if __name__ == '__main__':
    app.run_server(debug=True)
