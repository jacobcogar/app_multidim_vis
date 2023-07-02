#!/usr/bin/env python3.8.13
# Author: Jacob Cogar
# Date: 2022-11
#       
# Description:
#   Application for multidimensional visualization. Interactive 3D+ scatterplot with additional dimensions to be added by changing color scale and marker size. 
#   Includes option to export as HTML object for importing link in PowerPoint presentations.

# Imports

import io
import base64
from base64 import b64encode
from datetime import datetime
import math
import requests
from flask import Flask
import pandas as pd
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px

buffer = io.StringIO()

mountain_logo = "assets/mountain.png"

# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def parse_contents(contents, filename, date):
    """
        function for file uploading and pulling data into a pandas dataframe
        input parameters : contents, base64 decoded
                           filename,
                           date, date when file was last saved
    """
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), delimiter=",", thousands=",")
        elif 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), delimiter=",", thousands=",")
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df

server = Flask(__name__)
server.secret_key = "CogarDD"

app = dash.Dash(server=server, assets_folder='./assets')

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col([
                        html.Div('Data Democratization', style={'fontSize': 20, 'whiteSpace': 'nowrap', 'fontFamily': 'Lucida Console'}),
                    ], className = "ml-1 pr-2"
                    ),

                    dbc.Col([
                        html.Img(src=mountain_logo, height="40px"),
                    ], className="pl-2 pr-4"
                    ), 

                    dbc.Col([
                        html.Div("Visualization: 3D+ Interactive Plot", style={'fontSize': 16, 'whiteSpace': 'nowrap', 'fontFamily': 'Lucida Console'}),
                    ])
                ],
                align="center",
                no_gutters=True,
            )
        ),
    ],
    color="light",
    dark=False,
)

file_information = dbc.Row(
    [
        dbc.Button("README", id="open", size="md"),
            dbc.Modal(
            [
                dbc.ModalHeader("Data Visualization: 3D+ Interactive Plot"),
                dbc.ModalBody(
                [
                    html.Div("INSTRUCTIONS:"),
                    html.Div("Either drag and drop the data file (.csv format) into the respective area or \
                            select the file \
                            from the file explorer. The information of the loaded file will be displayed to \
                            the right. Select variables corresponding to the x, y, and z axes. The graph will auto-appear. \
                            To add more dimensions, you can optionally select variables to adjust \
                            symbol designations, marker color scale, and marker size. Marker opacity and max. size can be further customized. The interactive graph can be exported as an HTML object. \
                            This can be incorporated as a link in a PowerPoint presentation or can be shared. The link will open \
                            a browser window that displays the interactive graph you customized."),
                    html.Br(),
                    html.Div('An example plot (using the "Iris" dataset) can be toggled on and off. Its only purpose is to show you the capabilities of this tool.'),
                    html.Br(),
                    html.Div('Mouse Operation:'),
                    html.Div('1) Right click and hold to pan around the graph.'),
                    html.Div('2) Use the scroll-wheel to zoom in and out.'),
                    html.Div('3) Middle-click, hold, and move mouse up and down to slowly zoom in and out.'),
                    html.Div('4) Left-click to rotate graph. Rotate method varies based on plot toolbar on the top right.'),
                    html.Br(),  
                    html.Div('More information about the Plotly tool utilized here can be found in "LINKS".'),
                    html.Br(),
                    html.Div('Happy Plotting!')        
                ]),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close", className="ml-auto")
                ),
            ],
            id="modal",
            size='lg'),

        dbc.DropdownMenu(
            children=[
            dbc.DropdownMenuItem("3D-Plot Documentation", href="https://plotly.com/python/3d-scatter-plots/", target='_blank', style = {'fontSize':'12px'}),
            ],
            label="Links",
            nav=False,
            style={
                'fontSize':'12px',
            }
        ),

        dbc.Col(dbc.Spinner(
                children=[

                dcc.Upload(
                        id='upload-file',
                        children=html.Div([
                            'Drop or ',
                            html.A('Select File')
                        ]),
                        style={
                            'height': '34%',
                            'lineHeight': '34px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign':'center',
                        },
                        multiple=False
                ),
                
                ], size='xl', color='primary', type='border', fullscreen=True),   
        width = {'size' : 3, 'offset' : 0, 'order': 2},
        ),

        dbc.Col(html.Div(
                id="file-information", 
                children="file information",
                style={
                    'border':'solid 1px black',
                    'borderwidth':'1px',
                    'borderRadius':'5px',
                    'height':'35px',
                    'textAlign':'center',
                    'lineHeight':'35px'
                },
                ),  
        width = {'size' : True, 'offset' : 0, 'order': 4}),        

    ], className='h-75', no_gutters = True
)

html_bytes = buffer.getvalue().encode()
encoded = b64encode(html_bytes).decode()

functionality = dbc.Row(
    [
        dbc.Col(
            [
                html.Div(
                    [
                        html.Span('Select X-Axis Variable', style={'textDecoration':'underline'}),
                        html.Span(':  '),
                        html.Span('REQUIRED', style={'color':'red', 'fontSize':'70%'}),
                    ],
                    className = 'pb-1'
                ),
                dbc.Row(
                    dbc.Col(
                        dcc.Dropdown(id = 'select-x'), style = {'display':'block'},
                    ),
                    className = 'pb-3 pr-5 pl-4'
                ),
                html.Div(
                    [
                        html.Span('Select Y-Axis Variable', style={'textDecoration':'underline'}),
                        html.Span(':  '),
                        html.Span('REQUIRED', style={'color':'red', 'fontSize':'70%'}),
                    ],
                    className = 'pb-1'
                ),
                dbc.Row(
                    dbc.Col(
                        dcc.Dropdown(id = 'select-y'),
                    ),
                    className = 'pb-3 pr-5 pl-4'
                ),
                html.Div(
                    [
                        html.Span('Select Z-Axis Variable', style={'textDecoration':'underline'}),
                        html.Span(':  '),
                        html.Span('REQUIRED', style={'color':'red', 'fontSize':'70%'}),
                    ],
                    className = 'pb-1'
                ),
                dbc.Row(
                    dbc.Col(
                        dcc.Dropdown(id = 'select-z'),
                    ),
                    className = 'pb-5 pr-5 pl-4'
                ),
                html.Div(
                    [
                        html.Span('Select Symbol Variable', style={'textDecoration':'underline'}),
                        html.Span(':  '),
                        html.Span('optional', style={'color':'blue', 'fontSize':'80%'}),
                    ],
                    className = 'pb-1'
                ),
                dbc.Row(
                    dbc.Col(
                        dcc.Dropdown(id = 'symbol_var'),
                    ),
                    className = 'pb-3 pr-5 pl-4'
                ),
                html.Div(
                    [
                        html.Span('Select Color Scale Variable', style={'textDecoration':'underline'}),
                        html.Span(':  '),
                        html.Span('optional', style={'color':'blue', 'fontSize':'80%'}),
                    ],
                    className = 'pb-1'
                ),
                dbc.Row(
                    dbc.Col(
                        dcc.Dropdown(id = 'color_scale'),
                    ),
                    className = 'pb-3 pr-5 pl-4'
                ),
                html.Div(
                    [
                        html.Span('Select Marker Size Variable', style={'textDecoration':'underline'}),
                        html.Span(':  '),
                        html.Span('optional', style={'color':'blue', 'fontSize':'80%'}),
                    ],
                    className = 'pb-1'
                ),
                dbc.Row(
                    dbc.Col(
                        dcc.Dropdown(id = 'marker_size'),
                    ),
                    className = 'pb-5 pr-5 pl-4'
                ),
                html.Div(
                    [
                        html.Span('Select Marker Opacity', style={'textDecoration':'underline'}),
                        html.Span(':'),
                    ],
                    className = 'pb-1'
                ),
                dbc.Row(
                    dbc.Col(
                        dcc.Slider(id = 'opacity', min=0, max=1, updatemode='mouseup', step=0.1, marks={0:'0.0',0.2:'0.2',0.4:'0.4',0.6:'0.6',0.8:'0.8',1:'1.0'}, value=0.7),
                    ),
                    className = 'pb-3 pr-5 pl-4'
                ),
                html.Div(
                    [
                        html.Span('Select Max Marker Size', style={'textDecoration':'underline'}),
                        html.Span(':'),
                    ],
                    className = 'pb-1'
                ),
                dbc.Row(
                    dbc.Col(
                        dcc.Slider(id = 'max_marker', min=0, updatemode='mouseup', max=50, step=1, marks={0:'0',10:'10',20:'20',30:'30',40:'40',50:'50'}, value=18),
                    ),
                    className = 'pb-5 pr-5 pl-4'
                ),
                dbc.Row(
                        dbc.Col(
                            html.A(
                                dbc.Button("Download", id='html-object', outline=False, size='lg', n_clicks=0, block=True, color="primary", className='mr-1'),
                                id="download",
                                # href="data:text/html;base64," + encoded,
                                download="plotly_graph.html"
                            )
                        ),
                    className = 'pb-4 pr-5 pl-4'
                ),
                dbc.Row(
                        dbc.Col(
                            dbc.Button("Toggle Example", id='button-example', outline=False, size='lg', n_clicks=0, block=True, color="secondary", className='mr-1'),
                        ),
                    className = 'pb-5 pr-5 pl-4'
                ),
            ],
            width = {'size' : 2, 'offset' : 0},
            className = 'pt-4 pl-4 mt-5 ml-5',
            style={'backgroundColor': '#D3D3D3'}
        ),
        dbc.Col(
            dcc.Loading(
                dcc.Graph(id = 'graph-data', 
                    style={'display':'inline-block', 
                        'height':'90vh', 
                        'size': 9,
                        'width':'80vw'
                    }
                ),
            )
        ),
    ],
    no_gutters=True
)

hidden = dbc.Row(
    [   
        dbc.Col(
            dbc.Spinner(
                children=[
                    html.Div(id='hidden-dummy', style = {'display':'none'}),
                ], color='primary', type='border', fullscreen=True, spinner_style={'width':'7rem', 'height':'7rem'}
            ),
        ),
            html.Div(id="hidden-df", style={'display':'none'}),
            html.Div(id='hidden-file_name', style={'display':'none'})
    ]
)

app.layout = html.Div(
    [
        navbar, 
        file_information, 
        functionality, 
        hidden
    ], 
        className="container",
        style={'width':'100%', 'maxWidth':'unset'}
)

@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(Output('button-example', 'n_clicks'),
             [Input('select-x', 'value'),
              Input('select-y', 'value')])
def update_nclick(value,valueind):
    return 0

@app.callback([Output('select-x', 'options'),
               Output('file-information','children'),
               Output('hidden-df', 'children'),
               Output('hidden-dummy','children'),
               Output('hidden-file_name','children')],
              [
            #    Input('select-y', 'value'),
               Input('upload-file', 'contents'),
               Input('upload-file', 'filename'),
               Input('upload-file', 'last_modified')])
def update_output(contents, name, date):

    """ Callback for getting input file information and load dataframe """
    
    if contents:
        
        df = parse_contents(contents, name, date)
        # delete unnamed columns; may happen from csv saving from excel
        for column_name in list(df.columns):
            if "Unnamed" in column_name:
                del df[column_name]

        # df = df.dropna()

        # if label_y
        #     label_index = features.index(label)
        #     features.pop(label_index)

        variables = list(df.columns)

        dt_object = datetime.fromtimestamp(date)
        filename = 'File Uploaded: "' + str(name) + '" from: ' + str(dt_object)

    else:
        variables = []  
        df = pd.DataFrame({})
        dt_object = ""
        filename = ""

    return [{'label': k, 'value': k} for k in variables], filename, df.to_json(), "", filename


@app.callback(Output("select-y","options"),
              [Input("hidden-df", "children"),
               Input('select-x','value')])
def set_y(jsonified_df, label):

    if jsonified_df != None:
        dff = pd.read_json(jsonified_df)
        features = list(dff.columns)

        if label != None:
            label_index = features.index(label)
            features.pop(label_index)
    else:
        features = []

    return [{'label': k, 'value': k} for k in features]

@app.callback(Output("select-z","options"),
              [Input("hidden-df", "children"),
               Input('select-y','value'),
               Input('select-x','value')])
def set_z(jsonified_df, label_y, label_x):

    if jsonified_df != None:
        dff = pd.read_json(jsonified_df)
        features = list(dff.columns)
        if label_y != None and label_x != None:
            label_y_index = features.index(label_y)
            features.pop(label_y_index)
            if label_x != label_y:
                label_x_index = features.index(label_x)
                features.pop(label_x_index)
        elif label_y != None and label_x == None:
            label_y_index = features.index(label_y)
            features.pop(label_y_index)
        elif label_y == None and label_x != None:
            label_x_index = features.index(label_x)
            features.pop(label_x_index)

    else:
        features = []

    return [{'label': k, 'value': k} for k in features]

@app.callback(Output("symbol_var","options"),
              [Input("hidden-df", "children")])
def symbol_dim(jsonified_df):

    if jsonified_df != None:
        dff = pd.read_json(jsonified_df)
        features = list(dff.columns)
    else:
        features = []

    return [{'label': k, 'value': k} for k in features]

@app.callback(Output("color_scale","options"),
              [Input("hidden-df", "children")])
def color_dim(jsonified_df):

    if jsonified_df != None:
        dff = pd.read_json(jsonified_df)
        features = list(dff.columns)
    else:
        features = []

    return [{'label': k, 'value': k} for k in features]

@app.callback(Output("marker_size","options"),
              [Input("hidden-df", "children")])
def marker_dim(jsonified_df):

    if jsonified_df != None:
        dff = pd.read_json(jsonified_df)
        features = list(dff.columns)
    else:
        features = []

    return [{'label': k, 'value': k} for k in features]

@app.callback([Output("graph-data", "figure"),
               Output('button-example', 'children'),
               Output('download', 'href')],
              [Input('button-example', 'n_clicks'),
              Input("hidden-df","children"),
               Input("select-x","value"),
               Input("select-y","value"),
               Input("select-z", 'value'),
               Input('symbol_var', 'value'),
               Input('color_scale', 'value'),
               Input('marker_size', 'value'),
               Input("hidden-file_name","children"),
               Input('max_marker', 'value'),
               Input('opacity', 'value'),
               Input('html-object', 'n_clicks')])
def plot_graph(example, jsonified_df, x_var, y_var, z_var, symbol_var, color_var, marker_var, file_name, marker_size_input, opacity_input, downloaded):

    buffer = io.StringIO()

    if (x_var and y_var and z_var):
        df = pd.read_json(jsonified_df)

        selected_features = [x_var, y_var, z_var]
        df_select = df[selected_features]

        if (symbol_var != None and symbol_var != x_var and symbol_var != y_var and symbol_var != z_var):
            frames = [df_select, df[symbol_var]]
            df_select = pd.concat(frames, axis=1, join='inner')
        if (color_var != None and color_var != x_var and color_var != y_var and color_var != z_var):
            frames = [df_select, df[color_var]]
            df_select = pd.concat(frames, axis=1, join='inner')        
        if (marker_var != None and marker_var != x_var and marker_var != y_var and marker_var != z_var):
            frames = [df_select, df[marker_var]]
            df_select = pd.concat(frames, axis=1, join='inner')
        
        marker_var_update = marker_var

        # Scale the marker_var column so that size is obvious:
        if (marker_var != None):
            marker_avg = df_select[marker_var].mean()
            marker_std_dev = df_select[marker_var].std(axis=0, skipna=True)
            df_select['marker_var_update'] = (df_select[marker_var] - marker_avg) / marker_std_dev
            marker_min = df_select['marker_var_update'].min()
            marker_min_floor = math.floor(marker_min)

            df_select['marker_var_update'] = df_select['marker_var_update'] + abs(marker_min_floor)
            marker_var_update = 'marker_var_update'

        df_final = df_select.dropna()

        if df_final.shape[0] == 0:
            df = px.data.iris()
            trace_data = px.scatter_3d(df,
                            x = None, #'sepal_length',
                            y = None, #'sepal_width',
                            z = None, #'petal_width',
                            color='petal_length', 
                            size='petal_length', 
                            #title='Example Plot using "Iris" Dataset',
                            symbol='species', 
                            size_max=marker_size_input,
                            opacity=opacity_input
            )

            # tight layout
            trace_data.update_layout(margin=dict(l=40, r=30, b=30, t=40), 
                            coloraxis_colorbar=dict(yanchor="top", y=1, x=0,
                                    ticks="outside",
                            ),
                            title=dict(x=0.5),
                            title_font_color = 'blue',
                            title_font=dict(size=24),
                            font_color = 'blue'                                      
            )
        else:
            trace_data = px.scatter_3d(df_final, 
                                    x = x_var,
                                    y = y_var,
                                    z = z_var,
                                    color=color_var,
                                    symbol=symbol_var,
                                    size=marker_var_update,
                                    size_max=marker_size_input,
                                    opacity=opacity_input,
                                )

            trace_data.update_layout(margin=dict(l=20, r=20, b=20, t=40))
            trace_data.update_layout(margin=dict(l=40, r=30, b=30, t=40), 
                                            coloraxis_colorbar=dict(yanchor="top", y=1, x=0,
                                            ticks="outside",
                                            )
            )

        if marker_var == None:
            trace_data.update_traces(marker=dict(size=marker_size_input/3.6))

        trace_data.write_html(buffer)
        html_bytes = buffer.getvalue().encode()
        encoded = b64encode(html_bytes).decode()

        return trace_data, 'Toggle Example On', 'data:text/html;base64,' + encoded

    elif example != 0 and example % 2 == 1:
        df = px.data.iris()
        trace_data = px.scatter_3d(df,
                            x = 'sepal_length',
                            y = 'sepal_width',
                            z = 'petal_width',
                            color='petal_length', 
                            size='petal_length', 
                            title='Example Plot using "Iris" Dataset',
                            symbol='species', 
                            size_max=marker_size_input,
                            opacity=opacity_input
        )

        # tight layout
        trace_data.update_layout(margin=dict(l=40, r=30, b=30, t=40), 
                                coloraxis_colorbar=dict(yanchor="top", y=1, x=0,
                                        ticks="outside",
                                ),
                                title=dict(x=0.5),
                                title_font_color = 'blue',
                                title_font=dict(size=24),
                                font_color = 'blue'
        )

        if marker_var == None:
            trace_data.update_traces(marker=dict(size=marker_size_input/3.6))

        trace_data.write_html(buffer)
        html_bytes = buffer.getvalue().encode()
        encoded = b64encode(html_bytes).decode()

        return trace_data, 'Toggle Example Off', 'data:text/html;base64,' + encoded

    else:
        df = px.data.iris()
        trace_data = px.scatter_3d(df,
                            x = None, #'sepal_length',
                            y = None, #'sepal_width',
                            z = None, #'petal_width',
                            color='petal_length', 
                            size='petal_length', 
                            #title='Example Plot using "Iris" Dataset',
                            symbol='species', 
                            size_max=marker_size_input,
                            opacity=opacity_input
        )

        # tight layout
        trace_data.update_layout(margin=dict(l=40, r=30, b=30, t=40), 
                                coloraxis_colorbar=dict(yanchor="top", y=1, x=0,
                                        ticks="outside",
                                ),
                                title=dict(x=0.5),
                                title_font_color = 'blue',
                                title_font=dict(size=24),
                                font_color = 'blue'                                      
        )
        
        return trace_data, 'Toggle Example On', None

if __name__ == "__main__":
    app.run_server(debug=True)