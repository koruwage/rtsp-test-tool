import os
import cv2
import json
import subprocess
import numpy as np

import streamlit as st
import time

# colors for visualization for image visualization
COLORS = [(56, 56, 255), (151, 157, 255), (31, 112, 255), (29, 178, 255), (49, 210, 207), (10, 249, 72), (23, 204, 146),
          (134, 219, 61), (52, 147, 26), (187, 212, 0), (168, 153, 44), (255, 194, 0), (147, 69, 52), (255, 115, 100),
          (236, 24, 0), (255, 56, 132), (133, 0, 82), (255, 56, 203), (200, 149, 255), (199, 55, 255)]


if not os.path.exists("models/"):
    os.makedirs("models/")
model_list = [model_name.strip() for model_name in open("model_list.txt").readlines()]
st.set_page_config(page_title="YOLOv8 Processing App", layout="wide", page_icon="./favicon-yolo.ico")
st.title("YOLOv8 Processing App")
# create select box for selecting ultralytics YOLOv8 model
model_selectbox = st.empty()
model_select = model_selectbox.selectbox("Select Ultralytics YOLOv8 model", model_list)
print(f"Selected ultralytics YOLOv8 model: {model_select}")
# model = YOLO(f'models/{model_select}.pt')  # Model initialization
#tab_image, tab_video, tab_live_stream, tab_upload_model = st.tabs(["Image Processing", "Video Processing", "Live Stream Processing", "Upload Custom YOLOv8 Model"])
tab_live_stream, tab_upload_model = st.tabs(["Live Stream Processing", "Upload Custom YOLOv8 Model"])
#tab_live_stream = st.tabs(["Live Stream Processing"])

#"rtsp://admin4str:tapo@Str123@192.168.1.133:554/stream1"
#"rtsp://admin4str:tapo@Str123@192.168.1.134:554/stream1"

with tab_live_stream:
    st.header("Live Stream Processing using YOLOv8")
    CAM_ID = st.text_input("rtsp://admin4str:admin4pass@192.168.1.134:554/stream1")
    #if CAM_ID.isnumeric():
    #    CAM_ID = int(CAM_ID)
    
    CAM_ID = "rtsp://admin4str:admin4pass@192.168.1.134:554/stream1"

    #print(CAM_ID)
    
    col_run, col_details, col_test = st.columns(3)
    run = col_run.button("Click to Start Live Stream Processing")
    col_details.text("test data -TBC")
    test = col_test.button("connection testing to the camera feed")

    if test:
        print(CAM_ID)
        
    
    frame_skip = 60
    pop_up_flag = False

    FRAME_WINDOW = st.image([], width=1280)

    print(type(FRAME_WINDOW))

    if run:
        print("inside run")
        cam = cv2.VideoCapture(CAM_ID)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # tracker = DeepSort(max_age=5)

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

                    # image, result_list_json = image_processing(image, model, tracker=tracker)
                    # person_detected = [result for result in result_list_json if result.get('class') == 'truck' or result.get('class') == 'person']
                    # person_detected = [result for result in result_list_json if result.get('class') == 'person']

                    # print("frame_skip  = ", frame_skip)

                    # if person_detected and pop_up_flag == False:
                    #     frame_skip = 30
                    #     pop_up_flag = True
                    #     col_run.button("ignore alert")

                    #if pop_up_flag == True: 
                    FRAME_WINDOW.image(image, channels="BGR", width=1280)

        cam.release()
        # tracker.delete_all_tracks()

with tab_upload_model:
    st.header("Upload Custom YOLOv8 Model")
