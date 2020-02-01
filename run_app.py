from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from docopt import docopt
from apps.dashboard.boards import board1
from apps.dashboard.boards.board import board

board.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@board.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    print('REFRESHING??')
    if pathname == '/dashboard':
        return board1.layout
    else:
        return '404'

if __name__ == '__main__':
    docstr = """
    Usage:
        run_visualization_app.py [options]

    Options:
        -h, --help                  Print this message
        --port=<int>                The seed on our experiment [default: 8896]
        --debug                     With debug
    """
    args = docopt(docstr, version='v0.1')
    port = int(args['--port'])
    debug = bool(args['--debug'])
    board.run_server(debug=debug, host='localhost', port=port)
