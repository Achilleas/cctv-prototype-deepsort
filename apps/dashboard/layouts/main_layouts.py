from dash.dependencies import Input, Output, State
from plotly.graph_objs import *
import dash_html_components as html
import dash_core_components as dcc
from utils.app_utils import *
from apps.general.layouts import *
from apps.general.graph_utils import *
import dash
import dash_table
import pandas as pd

def menu_layout():
    button1 = get_button(id_='menu_button1', value='Button 1', background_colour='#FBFCFC')
    button2 = get_button(id_='menu_button2', value='Button 2', background_colour='#FBFCFC')
    button3 = get_button(id_='menu_button3', value='Button 3', background_colour='#FBFCFC')
    return html.Div([
        html.A(button1, href='/board1')])
#def get_banner(banner_title, logo):
#    title = html.Div(html.H2(banner_title))
#    img = html.Img(src='data:image/png;base64,{}'.format(logo), style={'height' : '100px', 'width' : '100px', 'position': 'relative'})
#    return html.Div([table_cell([img, title], [0.05,0.95])], className='banner')

##############################BOARD 2#############################
def filter_menu():
    #Filter by hours
    #Filter by class
    #Filter by video id
    name = 'filter_menu'
    divs = []
    date_picker = get_date_picker_range(id_=name + '_date_picker')
    class_drop = get_dropdown(id_=name + '_class', multi=False, options=['person', 'car'])
    video_id = get_dropdown(id_=name + '_video', multi=True, options=['cctv_0', 'cctv_1', 'cctv_2'])

    divs.append(table_cell([class_drop, video_id, date_picker], [0.4, 0.4, 0.2]))

    '''
    divs.append(html.Div(html.A(
                    'Download Result',
                    id=name + '-download',
                    download="temp_pickle.pkl",
                    href="",
                    target="_blank"
                )))
    '''
    divs.append(html.Div(dcc.Interval(id="refresh", interval=1*2000, n_intervals=0)))
    return html.Div(divs)

def perimeter_part():
    return html.Div(dcc.Graph(id='perimeter',
                                figure=build_perimeter_graph()))
    #build_trace_graph

def warnings_part():
    #[{'name': 'State', 'id': 'State'},
    #[{'State': 'California',
    #  'Number of Solar Plants': 289,
    #  'Installed Capacity (MW)': 4395,
    #  'Average MW Per Plant': 15.3,
    #  'Generation (GWh)': 10826},
    warning_columns = ['ALERT ID', 'DATE', 'TYPE', 'INFO']
    return html.Div(dash_table.DataTable(
        id = 'datatable',
        data=[{}],
        columns=[
            {'name': i, 'id': i} for i in warning_columns
        ],
        style_data_conditional=[
        #{
            #'if': {'row_id': 'person_reach'},
            #'backgroundColor': '#3D9970',
            #'color': 'white',
        #}
        ],
    ))



"""
html.Div(
    id="flight_info_table_outer",
    className="eight columns",
    children=dcc.Loading(
        id="table-loading",
        children=dash_table.DataTable(
            id="flights-table",
            columns=[
                {"name": i, "id": i}
                for i in [
                    "flightnum",
                    "dep_timestamp",
                    "arr_timestamp",
                    "origin_city",
                    "dest_city",
                ]
            ],
            filter_action="native",
            fill_width=True,
            data=[],
            style_as_list_view=True,
            style_header={
                "textTransform": "Uppercase",
                "fontWeight": "bold",
                "backgroundColor": "#ffffff",
                "padding": "10px 0px",
            },
            style_data_conditional=[
                {
                    "if": {"row_index": "even"},
                    "backgroundColor": "#f5f6f7",
                },
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#ffffff",
                },
            ],
                ),
"""

def image_2D_layout(img_width=300):
    divs = []

    input_text = html.Div('Input')
    label_text = html.Div('Label')
    pred_text = html.Div('Prediction')

    input_img = html.Img(id='image_2d_input', alt='input', style={'width': str(img_width) + 'px'})
    label_img = html.Img(id='image_2d_label', alt='label', style={'width': str(img_width) + 'px'})
    pred_img = html.Img(id='image_2d_pred',  alt='prediction', style={'width': str(img_width) + 'px'})

    divs.append(table_cell([input_text, label_text, pred_text], [0.3, 0.3, 0.4]))
    divs.append(table_cell([input_img, label_img, pred_img], [0.3, 0.3, 0.4]))

    return html.Div(divs)
