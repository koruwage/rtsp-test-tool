import cv2
import streamlit as st
import logging
import subprocess
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

frame_skip = 15

def ping_ip(ip_address):
    # Run the ping command
    process = subprocess.Popen(['ping', '-c', '4', ip_address])
    
def main():
 
    logging.error("DEBUG - loading")

    # Create text input boxes for the IP address and port
    ip_address = st.text_input("Enter the IP address of the camera:", "192.168.1.134")
    port = st.text_input("Enter the port of the camera:", "554")
    #rtsp_service = st.text_input("Enter the service of the camera:", "192.168.1.134:554")
    auth_user = st.text_input("Enter rtsp username:", "####")
    auth_password = st.text_input("Enter rtsp password:", "####")
    frame_skip = st.text_input("Enter number of frames to skip:", "15")

    CAM_ID = st.button("confirm")

    if CAM_ID:

        # rtsp_service = f"{ip_address}:{port}"
        # rtsp_string = f"rtsp://admin4str:admin4pass@{rtsp_service}/stream1"
        rtsp_string = f"rtsp://{auth_user}:{auth_password}@{ip_address}:{port}/stream1"

        
        cap = cv2.VideoCapture(rtsp_string)


        # Check if the camera is opened successfully
        if not cap.isOpened():
            st.error("Unable to open the camera")
            logging.error("Unable to open the camera")
            return

        # Set the video frame width and height
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # drop frame rate per second to a lower number
        # cap.set(cv2.CAP_PROP_FPS, 1)


        # Create a Streamlit window to display the camera feed
        st.title("Camera Feed")
        video_placeholder = st.empty()

        # Read and display frames from the camera
        i = 0
        while True:
            # Read a frame from the camera
            ret, frame = cap.read()

            if ret:
                i += 1
                if i < int(frame_skip):
                    #print("frame skiped = ", i, "/", frame_skip )                
                    pass
                else:
                    i = 0

                    if not ret:
                        st.error("Failed to read frame from camera")
                        logging.error("Failed to read frame from camera")
                        break

                    # Display the frame in the Streamlit window
                    video_placeholder.image(frame, channels="BGR")

        # Release the VideoCapture object and close the Streamlit window
        cap.release()

if __name__ == "__main__":

    main()
