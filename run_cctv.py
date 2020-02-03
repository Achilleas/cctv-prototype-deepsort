import os
import cv2
import time
import argparse
import torch
import numpy as np
from deep_sort_pytorch.utils.parser import get_config
from deep_sort_pytorch.VideoTracker import VideoTracker
from deep_sort_pytorch.Namespace import Namespace

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("VIDEO_PATH", type=str)
    parser.add_argument("--config_detection", type=str, default="deep_sort_pytorch/configs/yolov3.yaml")
    parser.add_argument("--config_deepsort", type=str, default="deep_sort_pytorch/configs/deep_sort.yaml")
    parser.add_argument("--ignore_display", dest="display", action="store_false", default=True)
    parser.add_argument("--frame_interval", type=int, default=1)
    parser.add_argument("--video_id", type=int, default=0)
    parser.add_argument("--display_width", type=int, default=1000)
    parser.add_argument("--display_height", type=int, default=800)
    parser.add_argument("--save_path", type=str, default="./demo/demo.avi")
    parser.add_argument("--cpu", dest="use_cuda", action="store_false", default=True)
    return parser.parse_args()

if __name__=="__main__":
    args = parse_args()
    cfg = get_config()
    cfg.merge_from_file(args.config_detection)
    cfg.merge_from_file(args.config_deepsort)

    print(args)
    print(cfg)
    with VideoTracker(cfg, args) as vdo_trk:
        vdo_trk.run()
