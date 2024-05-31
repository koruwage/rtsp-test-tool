import cv2
import streamlit as st
import logging
import subprocess
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ip_address_38_front = '192.168.1.134'
frame_skip = 15


def ping_ip(ip_address):
    # Run the ping command
    process = subprocess.Popen(['ping', '-c', '4', ip_address])
    
    # Log the output
    # logging.info(f"Ping output for {ip_address}:\n{stdout.decode('utf-8')}")
    # logging.info("Ping output for {ip_address}: okay")
    
    



def main():
    #// make sure my rtsp feed is accessible before executing the main function
    


    logging.error("initial loading up to show geenuka 111")

    # Create text input boxes for the IP address and port
    ip_address = st.text_input("Enter the IP address of the camera:", "192.168.1.134")
    port = st.text_input("Enter the port of the camera:", "554")
    rtsp_service = st.text_input("Enter the service of the camera:", "192.168.1.134:554")
    frame_skip = st.text_input("Enter the frame skip:", "15")

    CAM_ID = st.button("confirm ip address")
    #if st.button("Confirm IP address"):
    if CAM_ID:

        # rtsp_service = f"{ip_address}:{port}"
        rtsp_string = f"rtsp://admin4str:admin4pass@{rtsp_service}/stream1"

        #logging.error(rtsp_string, " <= rtsp string")

        # RTSP_SERVICE = st.text_input("192.168.1.134:554")
        # RTSP_STRING = "rtsp://admin4str:admin4pass@{RTSP_SERVICE}/stream1"
        # ping_ip(ip_address)

        #CAM_ID = st.button("rtsp://admin4str:admin4pass@{ip_address_38_front}:554/stream1")
        
        # Create a VideoCapture object to read from the camera
        #cap = cv2.VideoCapture("rtsp://admin4str:admin4pass@192.168.1.134:554/stream1")
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
                    # log current time stream
                    
                    # current_time = time.time()
                    # local_time = time.localtime(current_time) 
                    # formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
                    # print(f"Current Time: {formatted_time}")
                    
                    # print("frame dispaced = ", i, "/", frame_skip )
                    
                    # Check if the frame was successfully read

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