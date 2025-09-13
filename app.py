import streamlit as st
from ultralytics import YOLO
import cv2
import time
import os
import warnings

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

st.set_page_config(page_title="Fire Detection", layout="centered")

st.title("🔥 Real-Time Fire Detection")
st.markdown("Using a YOLO model to detect fire through your webcam.")

# Initialize session state variables
if 'detection_active' not in st.session_state:
    st.session_state.detection_active = False

# Load model with proper error handling
if 'model' not in st.session_state:
    model_path = 'best.pt'
    
    # If model doesn't exist, try to download it
    if not os.path.exists(model_path):
        st.info("Model file not found. Attempting to download...")
        try:
            import requests
            # Replace this URL with your actual model hosting URL
            model_url = "https://your-hosting-service.com/best.pt"  # You need to replace this
            
            with st.spinner("Downloading model..."):
                response = requests.get(model_url)
                response.raise_for_status()
                
                with open(model_path, 'wb') as f:
                    f.write(response.content)
                    
                st.success("Model downloaded successfully!")
        except Exception as e:
            st.error(f"❌ Could not download model: {e}")
            st.info("Please ensure 'best.pt' is available or provide a valid download URL")
            st.stop()
    
    # Load the model
    try:
        st.session_state.model = YOLO(model_path)
        st.success("✅ Model loaded successfully!")
            
            # Display model classes for debugging (only in expander)
            with st.expander("🔧 Developer Info", expanded=False):
                try:
                    classes = st.session_state.model.names
                    st.write(f"Model classes: {classes}")
                    
                    # Find fire class index
                    fire_class_idx = None
                    for idx, class_name in classes.items():
                        if 'fire' in class_name.lower():
                            fire_class_idx = idx
                            break
                    
                    if fire_class_idx is not None:
                        st.session_state.fire_class_idx = fire_class_idx
                        st.write(f"Fire class index: {fire_class_idx}")
                    else:
                        st.write("Fire class not found. Using class 0 as default.")
                        st.session_state.fire_class_idx = 0
                        
                except Exception as e:
                    st.write(f"Could not get model class info: {e}")
                    st.session_state.fire_class_idx = 0
                
        except Exception as e:
            st.error(f"❌ Error loading model: {str(e)}")
            st.stop()
    else:
        st.error(f"❌ Model file '{model_path}' not found!")
        st.info("Please ensure 'best.pt' is in the same directory as app.py")
        st.stop()

# Control buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("🎥 Start Detection", disabled=st.session_state.detection_active):
        st.session_state.detection_active = True
        st.rerun()

with col2:
    if st.button("⏹️ Stop Detection", disabled=not st.session_state.detection_active):
        st.session_state.detection_active = False
        st.rerun()

# Main detection logic
if st.session_state.detection_active:
    st.info("🔴 Detection is ACTIVE")
    
    # Create placeholders for dynamic content
    stframe = st.empty()
    progress_container = st.empty()
    message_container = st.empty()
    stats_container = st.empty()
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        st.error("❌ Cannot access webcam. Please check your camera permissions.")
        st.session_state.detection_active = False
        st.rerun()
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    frame_count = 0
    fire_detections = 0
    start_time = time.time()
    fire_class_idx = st.session_state.get('fire_class_idx', 0)
    
    # Main detection loop
    while st.session_state.detection_active:
        ret, frame = cap.read()
        if not ret:
            st.error("❌ Failed to access webcam.")
            break

        frame_count += 1
        
        try:
            results = st.session_state.model.predict(source=frame, imgsz=640, conf=0.6, verbose=False)
            annotated_frame = results[0].plot()

            # Check if fire is detected
            fire_detected = False
            confidence_scores = []
            detection_count = 0
            
            if len(results[0].boxes) > 0:
                for box in results[0].boxes:
                    if int(box.cls) == fire_class_idx:  # Use correct fire class index
                        fire_detected = True
                        confidence_scores.append(float(box.conf))
                        detection_count += 1
                        fire_detections += 1

            # Update progress bar
            with progress_container:
                if fire_detected:
                    max_confidence = max(confidence_scores)
                    st.progress(max_confidence, text=f"🔥 Fire Confidence: {max_confidence:.2f}")
                else:
                    st.progress(0, text="✅ No Fire Detected")

            # Only show message when fire is detected
            if fire_detected:
                max_conf = max(confidence_scores)
                with message_container:
                    st.error(f"🚨 FIRE DETECTED! Objects: {detection_count}, Confidence: {max_conf:.2f}")

            # Display statistics
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time if elapsed_time > 0 else 0
            
            with stats_container:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("FPS", f"{fps:.1f}")
                with col2:
                    st.metric("Frames", frame_count)
                with col3:
                    st.metric("Fire Alerts", fire_detections)
                with col4:
                    st.metric("Runtime", f"{elapsed_time:.1f}s")

            # Display the annotated frame - using width parameter to avoid deprecation warnings
            stframe.image(annotated_frame, channels="BGR", width=640)

        except Exception as e:
            st.error(f"❌ Error during detection: {str(e)}")
            break

        # Add a small delay to manage resource usage
        time.sleep(0.03)
    
    # Cleanup when loop ends
    cap.release()
    
    if not st.session_state.detection_active:
        st.success("✅ Detection stopped successfully.")

else:
    st.info("👆 Click 'Start Detection' to begin fire detection")
    
    # Display helpful information when not running
    st.markdown("""
    ### How it works:
    1. Click **Start Detection** to activate your webcam
    2. The YOLO model will analyze each frame for fire detection
    3. When fire is detected, you'll see:
       - A red alert message
       - Progress bar showing confidence level
       - Bounding boxes around detected fire areas
    4. Click **Stop Detection** to end the session
    
    ### Requirements:
    - Webcam access enabled
    - `best.pt` model file in the same directory
    - Good lighting conditions for optimal detection
    """)

# Add some styling
st.markdown("""
<style>
.stProgress > div > div > div > div {
    background-color: #ff4444;
}
</style>
""", unsafe_allow_html=True)