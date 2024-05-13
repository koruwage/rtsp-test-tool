import os
import cv2
import json
import subprocess
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results
from _collections import deque
from deep_sort_realtime.deepsort_tracker import DeepSort
from stqdm import stqdm
import streamlit as st
import time

# colors for visualization for image visualization
COLORS = [(56, 56, 255), (151, 157, 255), (31, 112, 255), (29, 178, 255), (49, 210, 207), (10, 249, 72), (23, 204, 146),
          (134, 219, 61), (52, 147, 26), (187, 212, 0), (168, 153, 44), (255, 194, 0), (147, 69, 52), (255, 115, 100),
          (236, 24, 0), (255, 56, 132), (133, 0, 82), (255, 56, 203), (200, 149, 255), (199, 55, 255)]


def result_to_json(result: Results, tracker=None):
    """
    Convert result from ultralytics YOLOv8 prediction to json format
    Parameters:
        result: Results from ultralytics YOLOv8 prediction
        tracker: DeepSort tracker
    Returns:
        result_list_json: detection result in json format
    """
    len_results = len(result.boxes)
    result_list_json = [
        {
            'class_id': int(result.boxes.cls[idx]),
            'class': result.names[int(result.boxes.cls[idx])],
            'confidence': float(result.boxes.conf[idx]),
            'bbox': {
                'x_min': int(result.boxes.data[idx][0]),
                'y_min': int(result.boxes.data[idx][1]),
                'x_max': int(result.boxes.data[idx][2]),
                'y_max': int(result.boxes.data[idx][3]),
            },
        } for idx in range(len_results)
    ]
    if result.masks is not None:
        for idx in range(len_results):
            result_list_json[idx]['mask'] = cv2.resize(result.masks.data[idx].cpu().numpy(), (result.orig_shape[1], result.orig_shape[0])).tolist()
            result_list_json[idx]['segments'] = result.masks.xyn[idx].tolist()
    if result.keypoints is not None:
        for idx in range(len_results):
            result_list_json[idx]['keypoints'] = result.keypoints.xyn[idx].tolist()
    if tracker is not None:
        bbs = [
            (
                [
                    result_list_json[idx]['bbox']['x_min'],
                    result_list_json[idx]['bbox']['y_min'],
                    result_list_json[idx]['bbox']['x_max'] - result_list_json[idx]['bbox']['x_min'],
                    result_list_json[idx]['bbox']['y_max'] - result_list_json[idx]['bbox']['y_min']
                ],
                result_list_json[idx]['confidence'],
                result_list_json[idx]['class'],
            ) for idx in range(len_results)
        ]
        tracks = tracker.update_tracks(bbs, frame=result.orig_img)
        for idx in range(len(result_list_json)):
            track_idx = next((i for i, track in enumerate(tracks) if track.det_conf is not None and np.isclose(track.det_conf, result_list_json[idx]['confidence'])), -1)
            if track_idx != -1:
                result_list_json[idx]['object_id'] = int(tracks[track_idx].track_id)
    return result_list_json


def view_result(result: Results, result_list_json, centers=None):
    """
    Visualize result from ultralytics YOLOv8 prediction using default visualization function
    Parameters:
        result: Results from ultralytics YOLOv8 prediction
        result_list_json: detection result in json format
        centers: list of deque of center points of bounding boxes
    Returns:
        result_image_default: result image from default visualization function
    """
    image = result.plot(labels=False, line_width=2)
    for result in result_list_json:
        class_color = COLORS[result['class_id'] % len(COLORS)]
        text = f"{result['class']} {result['object_id']}: {result['confidence']:.2f}" if 'object_id' in result else f"{result['class']}: {result['confidence']:.2f}"
        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)
        cv2.rectangle(image, (result['bbox']['x_min'], result['bbox']['y_min'] - text_height - baseline), (result['bbox']['x_min'] + text_width, result['bbox']['y_min']), class_color, -1)
        cv2.putText(image, text, (result['bbox']['x_min'], result['bbox']['y_min'] - baseline), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        if 'object_id' in result and centers is not None:
            centers[result['object_id']].append((int((result['bbox']['x_min'] + result['bbox']['x_max']) / 2), int((result['bbox']['y_min'] + result['bbox']['y_max']) / 2)))
            for j in range(1, len(centers[result['object_id']])):
                if centers[result['object_id']][j - 1] is None or centers[result['object_id']][j] is None:
                    continue
                thickness = int(np.sqrt(64 / float(j + 1)) * 2)
                cv2.line(image, centers[result['object_id']][j - 1], centers[result['object_id']][j], class_color, thickness)
    return image


def image_processing(frame, model, tracker=None, centers=None):
    """
    Process image frame using ultralytics YOLOv8 model and possibly DeepSort tracker if it is provided
    Parameters:
        frame: image frame
        model: ultralytics YOLOv8 model
        tracker: DeepSort tracker
        centers: list of deque of center points of bounding boxes
    Returns:
        result_image: result image with bounding boxes, class names, confidence scores, object masks, and possibly object IDs
        result_list_json: detection result in json format
    """
    results = model.predict(frame)
    result_list_json = result_to_json(results[0], tracker=tracker)
    result_image = view_result(results[0], result_list_json, centers=centers)
    return result_image, result_list_json



if not os.path.exists("models/"):
    os.makedirs("models/")
model_list = [model_name.strip() for model_name in open("model_list.txt").readlines()]
st.set_page_config(page_title="YOLOv8 Processing App", layout="wide", page_icon="./favicon-yolo.ico")
st.title("YOLOv8 Processing App")
# create select box for selecting ultralytics YOLOv8 model
model_selectbox = st.empty()
model_select = model_selectbox.selectbox("Select Ultralytics YOLOv8 model", model_list)
print(f"Selected ultralytics YOLOv8 model: {model_select}")
model = YOLO(f'models/{model_select}.pt')  # Model initialization
#tab_image, tab_video, tab_live_stream, tab_upload_model = st.tabs(["Image Processing", "Video Processing", "Live Stream Processing", "Upload Custom YOLOv8 Model"])
tab_live_stream, tab_upload_model = st.tabs(["Live Stream Processing", "Upload Custom YOLOv8 Model"])
#tab_live_stream = st.tabs(["Live Stream Processing"])

#"rtsp://admin4str:tapo@Str123@192.168.1.133:554/stream1"
#"rtsp://admin4str:tapo@Str123@192.168.1.134:554/stream1"

with tab_live_stream:
    st.header("Live Stream Processing using YOLOv8")
    CAM_ID = st.text_input("Enter a live stream source (number for webcam, RTSP or HTTP(S) URL):", "rtsp://admin4str:tapo@Str123@192.168.1.134:554/stream1")
    if CAM_ID.isnumeric():
        CAM_ID = int(CAM_ID)
    
    col_run, col_details = st.columns(2)
    run = col_run.button("Click to Start Live Stream Processing")
    
    col_details.text("test ======================== test")
    
    frame_skip = 30
    pop_up_flag = False

    FRAME_WINDOW = st.image([], width=1280)


    if run:
        cam = cv2.VideoCapture(CAM_ID)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


        tracker = DeepSort(max_age=5)

        i = 0
        while True:
            ret, image = cam.read()

            if ret:
                i += 1
                if i < frame_skip:                    
                    pass
                else:
                    i = 0
                    if not ret:
                        st.error("Failed to capture stream from this camera stream. Please try again.")
                        break

                    image, result_list_json = image_processing(image, model, tracker=tracker)
                    person_detected = [result for result in result_list_json if result.get('class') == 'truck' or result.get('class') == 'person']

                    print("frame_skip = ", frame_skip)

                    if person_detected and pop_up_flag == False:
                        frame_skip = 15
                        pop_up_flag = True
                        col_run.button("ignore alert")

                    if pop_up_flag == True: FRAME_WINDOW.image(image, channels="BGR", width=1280)

        cam.release()
        tracker.delete_all_tracks()

with tab_upload_model:
    st.header("Upload Custom YOLOv8 Model")
