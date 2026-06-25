import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import python_conversational_agent
import base64
import hashlib
from python_conversational_agent.chat_agent.chat_agent import ChatAgent
from python_conversational_agent.mascot.mascot_controller import MascotController
from python_conversational_agent.speech.app import AudioProcessor


# Paths

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
HTML_PATH = Path(__file__).parent.parent / "frontend" / "threejs_mascot.html"
PACKAGE_ROOT = Path(python_conversational_agent.__file__).parent.resolve()
ASSETS_MASCOT_DIR = PACKAGE_ROOT / "assets" / "mascot"

@st.cache_resource
def load_mascot_data():
    html_path = Path(__file__).parent.parent / "frontend" / "threejs_mascot.html"
    if not html_path.exists():
        return "", False

    with open(html_path, "r", encoding="utf-8") as f:
        mascot_html = f.read()

    glb_path = Path(__file__).parent / "static" / "mascot.glb"
    if glb_path.exists():
        with open(glb_path, "rb") as f:
            glb_data = f.read()
        glb_base64 = base64.b64encode(glb_data).decode("utf-8")
        glb_data_uri = f"data:application/octet-stream;base64,{glb_base64}"
        mascot_html = mascot_html.replace("GLB_DATA_URI_PLACEHOLDER", glb_data_uri)
        # Default to neutral emotion for static HTML structure
        mascot_html = mascot_html.replace("CURRENT_EMOTION_PLACEHOLDER", "neutral")
        return mascot_html, True
    else:
        return mascot_html, False

MASCOT_HTML, USE_3D = load_mascot_data()

if not USE_3D:
    if not HTML_PATH.exists():
        pass
    else:
        st.error("GLB file not found at static/mascot.glb")
    mascot_2d = MascotController(assets_dir=ASSETS_MASCOT_DIR)


def render_mascot(emotion: str):
    if USE_3D:
        # Render static mascot frame (cached so it never reloads or flashes)
        components.html(MASCOT_HTML, height=800)

        # Render a tiny helper script to post the emotion update dynamically
        js_code = f"""
            <script>
                const emotion = "{emotion}";
                const broadcast = () => {{
                    if (window.parent && window.parent.frames) {{
                        for (let i = 0; i < window.parent.frames.length; i++) {{
                            window.parent.frames[i].postMessage({{
                                type: 'SET_EMOTION',
                                emotion: emotion
                            }}, '*');
                        }}
                    }}
                }};
                broadcast();
                setTimeout(broadcast, 100);
                setTimeout(broadcast, 500);
            </script>
        """
        components.html(js_code, height=0, width=0)
    else:
        img_path = mascot_2d.get_image_path(emotion)
        if img_path.exists():
            st.image(str(img_path), width=250)
        else:
            st.warning(f"Missing 2D image: {img_path.name}")

@st.cache_resource(show_spinner="Ladataan äänimalleja...", max_entries=1)
def get_audio_processor():
    return AudioProcessor(whisper_model="base", compute_type="int8", piper_voice="en_US-amy-medium")

audio_processor = get_audio_processor()

# Main app

st.set_page_config(page_title="Conversational Agent", layout="wide")
st.title("Python Conversational Agent")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "emotion" not in st.session_state:
    st.session_state.emotion = "neutral"
if "waiting_for_response" not in st.session_state:
    st.session_state.waiting_for_response = False

if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None
if "response_audio" not in st.session_state:
    st.session_state.response_audio = None

with st.sidebar:

    render_mascot(st.session_state.emotion)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input area for user text and audio
user_input_text = st.chat_input("Type a message...")
audio_data = st.audio_input("Or speak...")

# Handle user text input
if user_input_text and not st.session_state.waiting_for_response:
    st.session_state.messages.append({"role": "user", "content": user_input_text})
    st.session_state.emotion = "listening"
    st.session_state.waiting_for_response = True
    st.rerun()

# Handle user st.audio input
if audio_data and not st.session_state.waiting_for_response:
    audio_bytes = audio_data.getvalue()
    current_hash = hashlib.sha256(audio_bytes).hexdigest()

    if current_hash != st.session_state.last_audio_hash:
        st.session_state.last_audio_hash = current_hash
        transcribed_text = audio_processor.transcribe(audio_bytes)

        if transcribed_text:
            st.session_state.messages.append({"role": "user", "content": transcribed_text})
            st.session_state.emotion = "listening"
            st.session_state.waiting_for_response = True
            st.rerun()

# Handle response (Ollama + Piper)
if st.session_state.waiting_for_response:
    agent = ChatAgent()
    last_user_msg = st.session_state.messages[-1]["content"]

    # Fetch text response
    response = agent.generate_response(last_user_msg)

    # Convert text response to audio with Piper
    audio_response_bytes = audio_processor.synthesize(response.text)

    st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.session_state.emotion = response.emotion
    # Save audio in session state
    st.session_state.response_audio = audio_response_bytes
    st.session_state.waiting_for_response = False
    st.rerun()

# Play audio response
if st.session_state.response_audio:
    st.audio(st.session_state.response_audio, format="audio/wav", autoplay=True)
    st.session_state.response_audio = None