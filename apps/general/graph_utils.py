import plotly.express as px
from dash.dependencies import Input, Output, State
from plotly.graph_objs import *
import dash_html_components as html
import dash_core_components as dcc
from utils.app_utils import *
import plotly.express as px
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

def build_perimeter_graph(video_ids=None, num_events=None):
    geojson = px.data.election_geojson()
    df = px.data.election()

    df.rename(columns={'Bergeron' : 'Occurences'})

    df['Occurences'] = 0

    if video_ids is not None and num_events is not None:
        video_ids = [int(video_id) for video_id in video_ids]
        for i, video_id in enumerate(video_ids):
            df.at[int(video_id), 'Occurences'] = num_events[i]

        df.loc[:, 'district'] = ['area_{}'.format(i) for i in range(len(df))]

        for i, video_id in enumerate(video_ids):
            df.at[int(video_id), 'district'] = 'cctv_{}'.format(video_id)

        for i, f in enumerate(geojson['features']):
            s = 'area_{}'.format(i)
            geojson['features'][i]['properties']['district'] = s
            geojson['features'][i]['id'] = str(df.at[i, 'district_id'])

        for video_id in video_ids:
            geojson['features'][video_id]['properties']['district'] = 'cctv_{}'.format(video_id)
            geojson['features'][video_id]['id'] = str(df.at[video_id, 'district_id'])

    fig = px.choropleth(df, geojson=geojson, color="Occurences",
                        locations="district", featureidkey="properties.district",
                        projection="mercator", color_continuous_scale='Reds'
                       )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def get_trace(x, y, err_y=None, name='', colour='#E9967A', visible=True, line_size=3, marker_size=5):
    """
    Args:
        x (list)       : list of x values
        y (list)       : list of y values
        err_y ()       : error on y values
        name (str)     : Label of trace (line)
        colour (str)   : Colour of trace
        visible (bool) : Show the trace
    Returns:
        returns plotly Trace
    """
    if err_y is None:
        err_y = []

    return Scatter(
        x=x,
        y=y,
        line=Line(
            color=colour,
            width=line_size
        ),
        marker=Marker(
            size=marker_size,
            color=colour
        ),
        hoverinfo='all',
        error_y=ErrorY(
            type='data',
            array=[0 for i in range(len(err_y))],
            thickness=1.5,
            width=2,
            color=colour
        ),
        visible=visible,
        mode='lines+markers',
        name=name,

    )

def get_bar_trace(x, y, name='', colour='#E9967A', visible=True, width=5, opacity=0.4):
    return Bar(
        x=x,
        y=y,
        visible=visible,
        name=name,
        width=width,
        opacity=opacity
    )


#######################################################################
############################BUILDING###################################
#######################################################################
def build_trace_graph(data, fig,
                        x_axis_type='Linear', y_axis_type='Linear',
                        x_title='', y_title='', properties={},
                        trace_type='line', legend_position='right'):
    """
    Args:
        data (dict)       : Dictionary containing keys as labels of each trace.
                            Each value contains dictionary with 'x', 'y' keys
                            corresponding to their values. Lists must be same length
        fig (Figure)      : Figure
        x_axis_type (str) : Linear/Log
        y_axis_type (str) : Linear/Log
        x_title (str)     : x axis title
        y_title (str)     : y axis title
    Returns plotly Figure
    """
    visibilities = get_trace_visibilities(fig)
    colour_list = get_hex_colour_list()
    ax_t = axis_transforms(x_axis_type, y_axis_type)
    colour_ind = 0
    traces = []

    for name in data.keys():
        x = ax_t['x'](data[name]['x'])
        y = ax_t['y'](data[name]['y'])

        visible = visibilities[name] if name in visibilities else True
        colour = colour_list[colour_ind]
        if trace_type == 'line':
            trace = get_trace(x, y, name=name, colour=colour, visible=visible, **properties)
        elif trace_type == 'bar':
            trace = get_bar_trace(x, y, name=name, colour=colour, visible=visible, **properties)
        if (len(colour_list) > colour_ind + 1):
            colour_ind += 1
        traces.append(trace)

    layout = get_default_graph_outline(x_title=x_title, y_title=y_title, legend_position=legend_position)
    fig = Figure(data=traces, layout=layout)
    return fig
