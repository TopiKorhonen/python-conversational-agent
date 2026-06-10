import streamlit as st
import cv2
import numpy as np
from camera_input_live import camera_input_live
from python_conversational_agent.vision import FacialAnalyzer

st.set_page_config(
    page_title="Emotion Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("Configuration")
detector_backend = st.sidebar.selectbox(
    "Detection Backend",
    options=["opencv", "ssd", "mediapipe"],
    index=0,
)

debounce_ms = st.sidebar.slider(
    "Camera Debounce (ms)",
    min_value=100,
    max_value=2000,
    value=300,
    step=50,
    help="Control how often the camera feeds updates to the server. Lower values are faster but consume more CPU/bandwidth."
)

# Cache FacialAnalyzer to avoid re-initializing models on every run
@st.cache_resource
def get_analyzer(backend):
    # We create a new instance when the backend changes, or reuse if same
    return FacialAnalyzer(detector_backend=backend)

# Re-create analyzer if backend selection changes
analyzer = get_analyzer(detector_backend)
# Update detector backend dynamically if needed
if analyzer.detector_backend != detector_backend:
    analyzer.detector_backend = detector_backend

col_feed, col_metrics = st.columns([3, 2], gap="large")

with col_feed:
    image_placeholder = st.empty()

with col_metrics:
    dominant_placeholder = st.empty() 
    emotions = ["happy", "sad", "neutral", "surprised", "confused", "tired"]
    
    emotion_placeholders = {}
    col1, col2 = st.columns(2)
    for idx, emotion in enumerate(emotions):
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            emotion_placeholders[emotion] = st.empty()
    
    dominant_info_placeholder = st.empty()

@st.fragment
def run_camera_and_analysis(image_placeholder, dominant_placeholder, emotion_placeholders, dominant_info_placeholder, debounce_ms):
    image_file = camera_input_live(debounce=debounce_ms, key="webcam")

    if image_file is not None:
        try:
            file_bytes = np.frombuffer(image_file.getvalue(), dtype=np.uint8)
            frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
            frame = cv2.flip(frame, 1)
            
            faces = analyzer.analyze_frame(frame)
            
            annotated_frame = frame.copy()
            
            dominant_emotion_name = "None detected"
            emotion_percentages = {e: 0.0 for e in emotions}
            confidence = 0.0

            for face in faces:
                box = face["box"]
                x, y, w, h = box["x"], box["y"], box["w"], box["h"]
                
                cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                
                dominant_emotion_name = face["dominant_mapped_emotion"]
                emotion_percentages = face["mapped_emotions"]
                confidence = face["face_confidence"]
                
                label = f"{dominant_emotion_name.upper()} (conf: {confidence:.2f})"
                cv2.putText(annotated_frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            
            image_placeholder.image(annotated_frame_rgb, width='stretch')
                
            if faces:
                dominant_placeholder.empty()
                for emotion in emotions:
                    pct = emotion_percentages.get(emotion, 0.0)
                    label = emotion.capitalize()
                    emotion_placeholders[emotion].metric(label, f"{pct:.1f}%")
                
                with dominant_info_placeholder.container():
                    col_dom, col_conf = st.columns(2)
                    col_dom.metric("Dominant Emotion", dominant_emotion_name.capitalize())
                    col_conf.metric("Confidence", f"{confidence:.2f}")
            else:
                dominant_placeholder.info("Looking for a face... Make sure you are well-lit and facing the camera.")
                for placeholder in emotion_placeholders.values():
                    placeholder.empty()
                dominant_info_placeholder.empty()
                    
        except Exception as e:
            st.error(f"Error processing frame: {e}")
    else:
        image_placeholder.info("Please allow camera access and stand in front of the webcam.")
        dominant_placeholder.info("Waiting for camera feed...")
        for placeholder in emotion_placeholders.values():
            placeholder.empty()
        dominant_info_placeholder.empty()

with col_feed:
    run_camera_and_analysis(image_placeholder, dominant_placeholder, emotion_placeholders, dominant_info_placeholder, debounce_ms)
