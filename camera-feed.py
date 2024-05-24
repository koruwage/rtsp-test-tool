import cv2
import streamlit as st

#// a simple camera feed using OpenCV and Streamlit see the feed on the browser
def main():
    # Create a VideoCapture object to read from the camera
    cap = cv2.VideoCapture("rtsp://admin4str:admin4pass@192.168.1.134:554/stream1")

    # Check if the camera is opened successfully
    if not cap.isOpened():
        st.error("Unable to open the camera")
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
    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        # Check if the frame was successfully read
        if not ret:
            st.error("Failed to read frame from camera")
            break

        # Display the frame in the Streamlit window
        video_placeholder.image(frame, channels="BGR")

    # Release the VideoCapture object and close the Streamlit window
    cap.release()

if __name__ == "__main__":
    main()