from dash.dependencies import Input, Output, State
from plotly.graph_objs import *
import dash_html_components as html
import dash_core_components as dcc
from utils.app_utils import *
from datetime import datetime as dt

def default_measure_graph_structure(title, figure_id, interval=5000,
                                        with_transforms=True, with_range_slider=False, with_slider=False,
                                        with_dropdown=False, dropdown_options=[['A','B']]):
    """
    Returns a standard graph structure
    Args:
        title (str)             : Title of graph
        figure_id (str)         : id of figure
        interval (int)          : update interval (ms)
        with_transforms (bool)  : include Linear/Log transforms on x/y axes
        with_slider     (bool)  : include slider to filter x values
        with_dropdown   (bool)  : include dropdown options
        dropdown_options (list) : list of dropdown options [options_list]
    """
    divs = []

    if with_transforms:
        divs = add_radio_transforms(divs, id_=figure_id)

    if with_range_slider:
        divs = add_range_slider(divs, id_=figure_id)

    if with_slider:
        divs = add_slider(divs, id_=figure_id)

    if with_dropdown:
        divs = add_dropdown(divs, ids_=[figure_id], options=dropdown_options)

    divs.append(html.Div([
        html.Div([
            html.H3(title)
        ], className='Title'),
        html.Div([
            dcc.Graph(id=figure_id),
        ], className='default_graph'),
        dcc.Interval(id=figure_id + '-update', interval=interval),
    ], className='row-default'))

    return html.Div(divs)

def add_radio_transforms(divs, id_):
    """
    Adds radio transforms ('Linear', 'Log') to list of divs
    Args:
        divs (list) : list divs to append radio transforms to
        id_   (str) : id to use for radio (id + '-xaxis-type'), (id + '-y_axis_type')
    Returns
        divs (list) : list of divs with appended radio transforms
    """
    x_radio = html.Div(
                dcc.RadioItems(
                    id=id_ + '-xaxis-type',
                    options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                    value='Linear',
                    labelStyle={'display': 'inline-block'}
                ),
                style={'display': 'inline-block'})

    y_radio = html.Div(
                dcc.RadioItems(
                    id=id_ + '-yaxis-type',
                    options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                    value='Linear',
                    labelStyle={'display': 'inline-block'}
                ),
                style={'display': 'inline-block'})

    x_radio_text = html.Div('x-axis')
    y_radio_text = html.Div('y-axis')

    empty_text = html.Div('')
    divs.append(html.Div(table_cell([x_radio_text, x_radio, empty_text],
                        [0.2, 0.2, 0.6])))
    divs.append(html.Div(table_cell([y_radio_text, y_radio, empty_text],
                        [0.2, 0.2, 0.6])))
    return divs

def add_range_slider(divs, id_):
    """
    Add range slider
    Args:
        divs (list) : list of divs to append
        id_   (str) : id_ to use for slider (id_ + '-slider')
    Returns:
        divs (list) : list of divs with appended slider
    """
    divs.append(html.Div([dcc.RangeSlider(
                        min=0,
                        max=100,
                        step=0.5,
                        value=[0, 100],
                        id=id_ + '-range_slider'
                    ),
                html.Div(id=id_ + '-range_slider_output')]))
    return divs

def add_radio(divs, ids_, options):
    """
    Add radio
    Args:
        divs (list) : list of divs to append
        id_   (str) : id_ to use for radio (id_ + '-radio')
    Returns:
        divs (list) : list of divs with appended radio
    """
    assert (len(ids_) == len(options))
    for i in range(len(ids_)):
        divs.append(
            html.Div(
                dcc.RadioItems(
                    id=ids_[i] + '-radio',
                    options=[{'label': j, 'value': j} for j in options[i]],
                    value=options[i][0],
                    labelStyle={'display': 'inline-block'}
                ),
                style={'width': '48%', 'display': 'inline-block'})
        )
    return divs

def add_dropdown(divs, ids_, options):
    """
    Add dropdown
    Args:
        divs (list) : list of divs to append
        id_   (str) : id_ to use for dropdown (id_ + '-dropdown')
    Returns:
        divs (list) : list of divs with appended dropdown
    """
    for i in range(len(ids_)):
        divs.append(
            html.Div(
                get_dropdown(id_=ids_[i], options=options[i])
            )
        )
    return divs

def add_slider(divs, id_):
    divs.append(get_slider(id_))
    divs.append(html.Div(id=id_ + '-slider_output'))
    return divs

def get_slider(id_, step=1, min=0, max=10, value=0):
    return dcc.Slider(
        id=id_ + '-slider',
        min=min,
        max=max,
        step=step,
        value=value
    )

def get_dropdown(id_, options, multi=False):
    """
    Args:
        id_      (str) : id_ to use for dropdown (id_ + '-dropdown')
        options (list) : list of options to include in dropdown
    Returns:
        dropdown div
    """
    return dcc.Dropdown(
        id=id_ + '-dropdown',
        options=[{'label': j, 'value': j} for j in options],
        value=options[0],
        multi=multi
    )



def table_cell(div_list, width_proportions):
    """
    Given a list of divs and list of width proportions return
    div displaying the divs in correct proportions horizontally.
    len(width_proportions) must be same len(div_list)

    Args:
        div_list : list of divs
        width_proportions : [0.1, 0.3, 0.6]
    Returns:
        returns horizontal proportions
    """
    inner_divs = []
    for i in range(len(div_list)):
        inner_divs.append(
            html.Div([div_list[i]],
            style = dict(
                width=str(width_proportions[i]*100) + '%',
                display = 'table-cell'
                        )
            )
        )

    return html.Div(
                inner_divs,
                style = dict(
                    width = '100%',
                    display = 'table',
                )
            )

def get_input(id_, placeholder='Enter a value...', value=''):
    """
    Args:
        id_         (str) : id (id_ + '-input')
        placeholder (str) : background value
        value       (str) : default value
    Returns:
        input field div
    """
    return dcc.Input(
        id=id_ + '-input',
        placeholder=placeholder,
        type='text',
        value=value
    )

def get_button(id_, value, background_colour=None, width=None):
    """
    returns button div
    Args:
        id_               (str) : id (id_ + '-button')
        value             (str) : string shown on button
        background_colour (str) : colour of button
        width           (float) : % width of button
    Returns:
        button div
    """
    if width is not None:
        width = str(100*float(width)) + '%'
        s = {'background' : background_colour,
             'width'              : width}
        return html.Button(value, id=id_ + '-button', style=s)
    else:
        s = {'background' : background_colour}
        return html.Button(value, id=id_ + '-button', style=s)
def default_markdown_layout(id_, interval=None):
    """
    Args:
        id_ (str)      : id (id_ + '-markdown')
        interval (int) : refresh interval
    Returns:
        markdown field div
    """
    if interval is None:
        return html.Div([dcc.Markdown(id=id_ + '-markdown')])
    else:
        return html.Div([dcc.Markdown(id=id_ + '-markdown'), dcc.Interval(id=id_ + '-update', interval=interval)])

def default_output_layout(id_, summary='Output'):
    """
    Args:
        id_     (str) : id (id_ + '-output')
        summary (str) : text on output div
    Returns:
        hide/show output div
    """
    return html.Details([
        html.Summary(summary),
        html.Div(id=id_ + '-output')
    ])

def default_hide_layout(div, value='testvalue'):
    return html.Details([
        html.Summary(value),
        div
    ])

def get_date_picker_range(id_):
    return html.Div(
            [dcc.DatePickerRange(
            id=id_,
            min_date_allowed=dt(2020, 2, 1),
            max_date_allowed=dt(2025, 12, 30),
            initial_visible_month=dt(2020, 2, 2),
            #end_date=dt(2020, 2, 3)
        ),
        #html.Div(id=id_ + '-output')
    ])
