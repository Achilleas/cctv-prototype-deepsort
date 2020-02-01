import dash
import os
from flask import send_from_directory, send_file

board = dash.Dash(__name__)
board.config['suppress_callback_exceptions'] = True
server = board.server
static_route = '/static/'
css_directory = 'apps/general/stylesheets'
#board.config.supress_callback_exceptions = True
#app.config.suppress_callback_exceptions = True

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                #"https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                #"https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"
                ]

local_css = ['wind.css']

'''
@server.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(server.root_path, 'static'), 'favicon.ico')
'''

@board.server.route('{}<path:path>'.format(static_route))
def static_file(path):
    static_folder = os.path.join(os.getcwd(), 'static')
    return send_from_directory(static_folder, path)

@board.server.route('{}<stylesheet>'.format(static_route))
def serve_stylesheet(stylesheet):
    if stylesheet not in local_css:
        raise Exception(
            '"{}" is excluded from the allowed static files'.format(
                stylesheet
            )
        )
    print('css directory: {}, stylesheet: {}'.format(css_directory, stylesheet))
    return send_from_directory(css_directory, stylesheet)

@board.server.route('/dash/urldownload')
def generate_report_url():
    print(os.getcwd())
    path = os.path.join(os.getcwd(), 'output.pkl')
    return send_file(path, attachment_filename='output.pkl', as_attachment=True)

for css in external_css:
    board.css.append_css({"external_url": css})
