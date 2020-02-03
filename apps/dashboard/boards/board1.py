from dash.dependencies import Input, Output, State
from plotly.graph_objs import *
import dash_html_components as html
import dash_core_components as dcc
import numpy as np
import base64
import time
import json
from datetime import datetime
from apps.dashboard.boards.board import board
from apps.general.BoardBlock import BoardBlock
from utils.app_utils import *
import redis
import yaml
import os
from apps.dashboard.layouts.main_layouts import *
from apps.general.layouts import *
from deep_sort_pytorch.RLogger import RLogger
from deep_sort_pytorch.general_utils import get_millis, get_millis_past, tracker_similarity_check
#from apps.general.graph_build import *

class MainDashboard(BoardBlock):
    def __init__(self, board, r, with_callbacks=True):
        self.board = board
        self.r = r
        self.rlogger = RLogger(r)
        self.layout = [ filter_menu(),
                        perimeter_part(),
                        warnings_part(),
                    ]
        self.measure_colours = get_hex_colour_list()
        if with_callbacks:
            self.setup_callbacks()

    def banner_layout(self):
        return html.Div([
            get_banner('Experiment Info', self.logo)
        ])

    def callbacks(self, app):
        @board.callback(Output('perimeter', 'figure'),
                        [Input('filter_menu_date_picker', 'start_date'),
                        Input('filter_menu_date_picker', 'end_date'),
                        Input('filter_menu_class-dropdown', 'value'),
                        Input('filter_menu_video-dropdown', 'value')],
                        [State('perimeter', 'figure')])
        def update_perimeter_graph(start_date, end_date, class_str, video_ids_str, fig):
            if isinstance(video_ids_str, str):
                video_ids_str = [video_ids_str]

            if start_date is not None:
                start_millis = datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000
            else:
                start_millis = 0
            if end_date is not None:
                end_millis = datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000
            else:
                end_millis = 99999999999999999

            video_ids_num = [video_id_str.split('_')[-1] for video_id_str in video_ids_str]
            num_events_l = []
            video_id_l = []
            for video_id in np.sort(video_ids_num):
                events_l = self.rlogger.get_interval_events(start_millis, end_millis, class_id=class_str, video_id=video_id)
                num_events_l.append(len(events_l))
                video_id_l.append(video_id)

            return build_perimeter_graph(video_ids=video_id_l, num_events=num_events_l)

        @board.callback(Output('datatable', 'data'),
                        [Input('refresh', 'n_intervals')],
                        [State('datatable', 'data'),
                         State('filter_menu_class-dropdown', 'value'),
                         State('filter_menu_video-dropdown', 'value')])
        def update_datatable(n_intervals, data, class_str, video_ids_str):
            if isinstance(video_ids_str, str):
                video_ids_str = [video_ids_str]
            time.sleep(1)
            #print('--------\n\n\n\n\n\n\n\n')
            alert_ids = []
            for r in data:
                if 'ALERT ID' in r.keys():
                    alert_ids.append(r['ALERT ID'])

            print('ALERT IDS ALREADY UP', alert_ids)
            video_ids_num = [video_id_str.split('_')[-1] for video_id_str in video_ids_str]

            #Was a human seen in camera 5 the last minute?
            human_trigger_video_id = 3

            if 'cctv_{}'.format(human_trigger_video_id) not in alert_ids:
                #print('I SHOULD BE HERE MAN')
                human_trigger_event_l = self.rlogger.get_interval_events(get_millis_past(60), None, class_id='car', video_id=human_trigger_video_id)
                human_trigger_details_l = self.rlogger.get_event_details(human_trigger_event_l)
                #print(human_trigger_event_l)
                if len(human_trigger_event_l) > 0:
                    #print('PRESENCE TRIGGER DETAILS L', human_trigger_details_l)

                    data.append({'ALERT ID' : 'cctv_{}'.format(human_trigger_video_id),
                                'DATE' : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                'TYPE' : 'detection_trigger',
                                'INFO' : 'Object detected: CAR'})


            #For camera 6, I have expectations of vectors in which the people will approach (b-l to t-r)
            #Preset start locations and distance metrics
            #Extract locations of trigger
            direction_video_id = 6

            print('alrert ids????')
            if 'cctv_{}'.format(direction_video_id) not in alert_ids:
                pos_trigger_event_l = self.rlogger.get_interval_events(get_millis_past(60), None, class_id='person', video_id=direction_video_id)
                #print('POSITION TRIGGER EVENT LIST:', pos_trigger_event_l)

                pos_trigger_details_l = self.rlogger.get_event_details(pos_trigger_event_l)

                #print('HOW MANY CAMERA 6 PERSONSSS', len(pos_trigger_event_l))
                num_people = len(pos_trigger_event_l)
                if len(pos_trigger_event_l) > 0:
                    #print('ALL DETAILS TO CHECK FOR ERROR', pos_trigger_details_l)
                    max_y, max_x, channels = self.rlogger.get_video_size(direction_video_id)
                    #Expectation:
                    ref_vec_l = [[0, max_y]]
                    ref_loc_l = [[1, -1]]
                    img_shape=[max_y, max_x, channels]

                    failed_counter = 0
                    passed_counter = 0
                    for detail_d in pos_trigger_details_l:
                        #print('NOW LOOKIG AT:', detail_d)
                        rectangle_l = json.loads(detail_d['rectangle_l'])
                        if len(rectangle_l) < 5:
                            print('Skipping for now', detail_d)
                            continue
                        #print('NOT SKIPPING THIS ONE')
                        passed_threshold, similarity_val = tracker_similarity_check(ref_loc_l, ref_vec_l, rectangle_l, img_shape, threshold=0.3)
                        #print('PASSED:', passed_threshold, 'SIMILARITY:', similarity_val)
                        if passed_threshold:
                            passed_counter += 1
                        else:
                            failed_counter += 1
                        total_checked = passed_counter + failed_counter

                        if failed_counter == 1:
                            data.append({'ALERT ID' : 'cctv_{}'.format(direction_video_id),
                                        'DATE' : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                        'TYPE' : 'walk_similarity_BELOW_LIMIT',
                                        'INFO' : 'Number objects: {}, PASSED: {} FAILED: {}, NO INFO {}:'.format(
                                                        num_people,
                                                        passed_counter,
                                                        failed_counter,
                                                        num_people - passed_counter-failed_counter)})
                            break
            #print('DATA STATE:', data)
            return data

config_path='deep_sort_pytorch/configs/redis_config.yml'
with open(config_path, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
    redis_init = cfg['redis_init']
    host = redis_init[0]
    port = redis_init[1]
    password = redis_init[2]

r = redis.StrictRedis(host=host, port=port, db=0, charset="utf-8", decode_responses=True, password=password)
# creating a new MyBlock will register all callbacks
block = MainDashboard(board=board, r=r)

layout = block.layout
