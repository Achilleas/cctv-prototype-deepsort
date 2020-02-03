## About

A small 1-day prototype of cctv camera tracking cars and humans.

- Run script for different video_id (representing different cctv camera)
- Store in Redis database (should be easy to change)
- Visualization dashboard prototype for summaries
  - filtering on different objects, cctv and time intervals
  - example map of where cctv is and its occurences
  - can add conditions for warnings on specific video_id (should be coded in). e.g. if car passed through show warning in dashboard

## Details
- Python 3, PyTorch
- Tracking from pytorch deepsort: https://github.com/ZQPei/deep_sort_pytorch (with a few edits)
- Pre-trained net: YOLOv3
- Dash/Plotly for visualization dashboard



## Setup and Run

### 1: Pytorch deepsort:

2. Download YOLOv3 parameters
```
cd detector/YOLOv3/weight/
wget https://pjreddie.com/media/files/yolov3.weights
wget https://pjreddie.com/media/files/yolov3-tiny.weights
cd ../../../
```

3. Download deepsort parameters ckpt.t7
```
cd deep_sort/deep/checkpoint
# download ckpt.t7 from
https://drive.google.com/drive/folders/1xhG0kRH1EX5B9_Iz8gQJb7UNnn_riXi6 to this folder
cd ../../../
```  

4. Compile nms module
```bash
cd detector/YOLOv3/nms
sh build.sh
cd ../../..
```
### 2: Database and Dashboard
- Run Redis server
- Run dashboard app.py (/dashboard)

### 3: Run
```
usage: python cctv_run.py VIDEO_PATH
                                [--help]
                                [--frame_interval FRAME_INTERVAL]
                                [--config_detection CONFIG_DETECTION]
                                [--config_deepsort CONFIG_DEEPSORT]
                                [--video_id CCTV_VIDEO_ID]
                                [--ignore_display]
                                [--display_width DISPLAY_WIDTH]
                                [--display_height DISPLAY_HEIGHT]
                                [--save_path SAVE_PATH]          
                                [--cpu]          
```

### 4: Example outputs
Example prediction
![Example prediction 1](demo/predict_1.gif)
![Example prediction 2](demo/predict_2.gif)

Example visualization
![Visualization app](demo/visualization_app.png)
