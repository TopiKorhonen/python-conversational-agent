import time

import streamlit as st
from pathlib import Path
import python_conversational_agent

from python_conversational_agent.chat_agent.chat_agent import ChatAgent
from python_conversational_agent.mascot.mascot_controller import MascotController

# Path setup – assets inside the package
PACKAGE_ROOT = Path(python_conversational_agent.__file__).parent.resolve()
ASSETS_MASCOT_DIR = PACKAGE_ROOT / "assets" / "mascot"

agent = ChatAgent()
mascot = MascotController(assets_dir=ASSETS_MASCOT_DIR)


# Sidebar with mascot
with st.sidebar:
    st.header("Mascot view")
    mascot_placeholder = st.empty()

# Main chat area
st.title("Python Conversational Agent")

# Initialise session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "emotion" not in st.session_state:
    st.session_state.emotion = "neutral"
if "emotion_set_time" not in st.session_state:
    st.session_state.emotion_set_time = time.time()
if "neutral_after_seconds" not in st.session_state:
    st.session_state.neutral_after_seconds = 5
if "thinking_delay_seconds" not in st.session_state:
    st.session_state.thinking_delay_seconds = 1.0
if "thinking_state" not in st.session_state:
    st.session_state.thinking_state = "idle"
if "waiting_for_response" not in st.session_state:
    st.session_state.waiting_for_response = False

# Return to neutral after x seconds
def reset_emotion():
    now = time.time()
    if not st.session_state.waiting_for_response and st.session_state.emotion != "neutral" and (
        now - st.session_state.emotion_set_time
    ) >= st.session_state.neutral_after_seconds:
        st.session_state.emotion = "neutral"
        st.session_state.emotion_set_time = now

# Function to update the sidebar mascot image
def update_mascot_image():
    img_path = mascot.get_image_path(st.session_state.emotion)
    if img_path.exists():
        mascot_placeholder.image(str(img_path), width=250)
    else:
        mascot_placeholder.warning(f"Missing: {img_path.name}")

# Reset to neutral if the emotion has been active too long
reset_emotion()

# Display current mascot emotion in sidebar
update_mascot_image()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
user_input = st.chat_input("Type a message...")

# Phase 1: user submits a message -> show "listening" emote immediately
if user_input and not st.session_state.waiting_for_response:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.emotion = "listening"
    st.session_state.emotion_set_time = time.time()
    st.session_state.thinking_state = "pending"
    update_mascot_image()
    st.session_state.waiting_for_response = True
    st.rerun()

# Phase 2: generate AI response and update final emotion
if st.session_state.waiting_for_response:
    last_user_msg = st.session_state.messages[-1]["content"]

    if st.session_state.thinking_state == "pending":
        st.session_state.emotion = "thinking"
        st.session_state.emotion_set_time = time.time()
        st.session_state.thinking_state = "active"
        update_mascot_image()
        st.rerun()

    with st.spinner("Thinking..."):
        time.sleep(st.session_state.thinking_delay_seconds)
        response = agent.generate_response(last_user_msg)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.session_state.emotion = response.emotion
    st.session_state.emotion_set_time = time.time()
    st.session_state.thinking_state = "idle"
    update_mascot_image()
    st.session_state.waiting_for_response = False
    st.rerun()