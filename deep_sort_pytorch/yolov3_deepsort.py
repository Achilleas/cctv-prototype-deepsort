import os
import cv2
import time
import argparse
import torch
import numpy as np

from general_utils import get_millis, get_class_from_id, extract_rectangle_centers
from detector import build_detector
from deep_sort import build_tracker
from utils.draw import draw_boxes, draw_lines
from utils.parser import get_config

import redis
from RLogger import RLogger
import yaml

class VideoTracker(object):
    def __init__(self, cfg, args):
        self.cfg = cfg
        self.args = args
        use_cuda = args.use_cuda and torch.cuda.is_available()
        #if not use_cuda:
        #    raise UserWarning("Running in cpu mode!")
        print('Running in cpu mode..')
        if args.display:
            cv2.namedWindow("test", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("test", args.display_width, args.display_height)

        self.vdo = cv2.VideoCapture()
        self.detector = build_detector(cfg, use_cuda=use_cuda)
        self.deepsort = build_tracker(cfg, use_cuda=use_cuda)
        self.class_names = self.detector.class_names

        self.rlogger = self.getRLogger()
        self.video_id = 1

        self.tracking_dict = {}

    def __enter__(self):
        assert os.path.isfile(self.args.VIDEO_PATH), "Error: path error"
        self.vdo.open(self.args.VIDEO_PATH)
        self.im_width = int(self.vdo.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.im_height = int(self.vdo.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if self.args.save_path:
            fourcc =  cv2.VideoWriter_fourcc(*'MJPG')
            self.writer = cv2.VideoWriter(self.args.save_path, fourcc, 20, (self.im_width,self.im_height))

        assert self.vdo.isOpened()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type:
            print(exc_type, exc_value, exc_traceback)

    def apply_track_step(self, identities, class_ids, rectangle_l):
        print(rectangle_l)
        for i, rectangle in enumerate(rectangle_l):
            identity = identities[i]
            idn = identity
            class_id = class_ids[i]

            if idn not in self.tracking_dict.keys():
                self.tracking_dict[idn] = {'video_id' : self.video_id,
                                                'time_start' : get_millis(),
                                                'time_end' : None,
                                                'rectangle_l' : [],
                                                'class_id' : get_class_from_id(int(class_id)),
                                                'frames_rem' : 2,
                                                'redis_id' : None}

                redis_id = self.rlogger.record_tracked_object(video_id=self.tracking_dict[idn]['video_id'],
                                            time_start=self.tracking_dict[idn]['time_start'],
                                            time_end=self.tracking_dict[idn]['time_start'], #not a bug don't worry self
                                            rectangle_l=self.tracking_dict[idn]['rectangle_l'],
                                            class_id = self.tracking_dict[idn]['class_id'])
                self.tracking_dict[idn]['redis_id'] = redis_id

            redis_id = self.tracking_dict[idn]['redis_id']

            self.tracking_dict[idn]['rectangle_l'].append([int(v) for v in rectangle])
            self.tracking_dict[idn]['time_end'] = get_millis()

            #Update time end and rectangle_l to include latest
            self.rlogger.update_tracked_object(redis_id=redis_id, update_d={'time_end' : self.tracking_dict[idn]['time_end'],
                                                                            'rectangle_l' : self.tracking_dict[idn]['rectangle_l']})

        print('IDENTITIES THIS STEP:', identities)
        print('IDENTITIES IN TRACKING DITC', list(self.tracking_dict.keys()))
        not_tracked_idns = list(set(self.tracking_dict.keys()) - set(identities))
        print('NOT TRACKED:', not_tracked_idns)
        for not_tracked_idn in not_tracked_idns:
            #Any identity not tracked yet has -1 counter
            self.tracking_dict[not_tracked_idn]['frames_rem'] -= 1

            if self.tracking_dict[not_tracked_idn]['frames_rem'] <= 0:
                print('REMOVING IDENTITY', not_tracked_idn)
                del self.tracking_dict[not_tracked_idn]

    def run(self):
        idx_frame = 0
        step_num = 0

        #Register frame
        self.rlogger.record_video_size(self.video_id, [self.im_height, self.im_width, 3])
        print('VIDEO SIEZE?', self.rlogger.get_video_size(self.video_id))
        #record_video_size
        #get_video_size
        while self.vdo.grab():
            idx_frame += 1
            if idx_frame % self.args.frame_interval:
                continue
            step_num += 1
            start = time.time()
            _, ori_im = self.vdo.retrieve()
            im = cv2.cvtColor(ori_im, cv2.COLOR_BGR2RGB)

            # do detection
            bbox_xywh, cls_conf, cls_ids = self.detector(im)

            #print('CONF??', cls_conf)
            #print(len(cls_conf))
            #print(len(cls_ids))
            if bbox_xywh is not None:
                # select person class
                mask = cls_ids==0

                bbox_xywh = bbox_xywh[mask]
                bbox_xywh[:,3:] *= 1.2 # bbox dilation just in case bbox too small
                cls_conf = cls_conf[mask]

                mask_w = np.where(mask == 1)
                # do tracking
                outputs = self.deepsort.update(bbox_xywh, cls_conf, im)

                #Apply tracking step and draw boxes and lines
                if len(outputs) > 0:
                    bbox_xyxy = outputs[:,:4]
                    identities = outputs[:,-1]

                    self.apply_track_step(identities=identities, class_ids=cls_ids, rectangle_l=bbox_xyxy)

                    #Draw boxes
                    ori_im = draw_boxes(ori_im, bbox_xyxy, identities)

                    # Draw tracking line
                    for idn in self.tracking_dict.keys():
                        rectangle_l = self.tracking_dict[idn]['rectangle_l']
                        center_l = extract_rectangle_centers(rectangle_l)
                        if idn == 11:
                            print('step num:', step_num)
                            print('HELLLOOOOO')
                            print('WHAAAA', center_l)
                            print('DETAILS', self.tracking_dict[idn])
                        ori_im = draw_lines(ori_im, center_l, idn)
            end = time.time()
            print("time: {:.03f}s, fps: {:.03f}".format(end-start, 1/(end-start)))

            print('ORI IMAGE SHAPE', ori_im.shape)
            if self.args.display:
                cv2.imshow("test", ori_im)
                cv2.waitKey(1)

            if self.args.save_path:
                self.writer.write(ori_im)

    def getRLogger(self):
        config_path='configs/redis_config.yml'
        with open(config_path, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
            redis_init = cfg['redis_init']
            host = redis_init[0]
            port = redis_init[1]
            password = redis_init[2]

        r = redis.StrictRedis(host=host, port=port, db=0, charset="utf-8", decode_responses=True, password=password)
        rlogger = RLogger(r=r)

        return rlogger

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("VIDEO_PATH", type=str)
    parser.add_argument("--config_detection", type=str, default="./configs/yolov3.yaml")
    parser.add_argument("--config_deepsort", type=str, default="./configs/deep_sort.yaml")
    parser.add_argument("--ignore_display", dest="display", action="store_false", default=True)
    parser.add_argument("--frame_interval", type=int, default=1)
    parser.add_argument("--display_width", type=int, default=800)
    parser.add_argument("--display_height", type=int, default=600)
    parser.add_argument("--save_path", type=str, default="./demo/demo.avi")
    parser.add_argument("--cpu", dest="use_cuda", action="store_false", default=True)
    return parser.parse_args()


if __name__=="__main__":
    args = parse_args()
    cfg = get_config()
    cfg.merge_from_file(args.config_detection)
    cfg.merge_from_file(args.config_deepsort)

    with VideoTracker(cfg, args) as vdo_trk:
        vdo_trk.run()
