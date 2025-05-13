import streamlit as st
from ultralytics import YOLO
import cv2
import time

st.set_page_config(page_title="Fire Detection", layout="centered")

st.title("🔥 Real-Time Fire Detection")
st.markdown("Using a YOLO model to detect fire through your webcam.")

if 'model' not in st.session_state:
    st.session_state.model = YOLO('best.pt')

start_button = st.button("Start Detection")

if start_button:
    stframe = st.empty()
    cap = cv2.VideoCapture(0)

    stop_button = st.button("Stop Detection", key="stop_button")  # Unique key for stop button
    fire_detected = False  # To track fire detection status
    
    # Create a progress bar
    progress = st.progress(0)  # Initial progress bar value set to 0 (No fire)

    fire_message = st.empty()  # To display the fire detection status message

    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to access webcam.")
            break

        results = st.session_state.model.predict(source=frame, imgsz=640, conf=0.6, verbose=False)
        annotated_frame = results[0].plot()

        # Check if fire is detected
        fire_detected = False
        for result in results[0].boxes.cls:
            if result == 0:  # Assuming class 0 corresponds to 'fire' in your model
                fire_detected = True
                break

        # Update progress bar and message based on detection status
        if fire_detected:
            progress.progress(100)  # Full progress bar indicates fire detected
            fire_message.write("🔥 Fire Detected!")
        else:
            progress.progress(0)  # No progress bar means no fire detected
            fire_message.write("No Fire Detected")

        # Display the annotated frame with detection
        stframe.image(annotated_frame, channels="BGR")

        # Check if the stop button is pressed and break the loop
        if stop_button:
            cap.release()
            st.success("Detection stopped.")
            break

        time.sleep(0.03)  # Add a small delay to manage resource usage
