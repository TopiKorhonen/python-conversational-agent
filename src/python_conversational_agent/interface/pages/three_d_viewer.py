import os
import streamlit as st
import streamlit.components.v1 as components

# Configure page settings
st.set_page_config(
    page_title="Three.js 3D Model Viewer",
    page_icon="🦊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# # Custom premium styling for the page
# st.markdown("""
# <style>
#     .main {
#         background-color: #0f172a;
#         color: #f8fafc;
#     }
#     .stRadio > label {
#         color: #94a3b8 !important;
#         font-weight: 600 !important;
#     }
#     .stRadio div[role="radiogroup"] {
#         background-color: #1e293b;
#         padding: 10px;
#         border-radius: 8px;
#         border: 1px solid #334155;
#     }
#     h1, h2, h3 {
#         color: #f8fafc !important;
#         font-family: 'Outfit', sans-serif;
#     }
#     .reportview-container {
#         background: #0f172a;
#     }
#     /* Add subtle shadow and border to iframe container */
#     iframe {
#         border-radius: 12px;
#         box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
#         border: 1px solid #334155 !important;
#     }
#     .badge {
#         background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
#         color: white;
#         padding: 4px 8px;
#         border-radius: 4px;
#         font-size: 12px;
#         font-weight: bold;
#     }
# </style>
# """, unsafe_allow_html=True)

from python_conversational_agent.interface.component_decl import threejs_viewer_component

# Helper to load and render the custom Three.js component
def render_threejs_viewer(animation_name: str):
    """
    Renders the custom Three.js component.
    Streamlit component rendering passes `animation_name` to the iframe, allowing real-time
    communication and cross-fading without reloading the page.
    """
    # Render component and pass args
    return threejs_viewer_component(animation=animation_name, key="threejs_viewer_comp")

# Layout structure
st.title("🦊 Three.js 3D Model Viewer")
st.markdown("Experience smooth real-time animation cross-fading using Three.js and a custom Streamlit component.")

# Sidebar Configuration
st.sidebar.header("Viewer Controls")

# Initialize session state for active animation
if "active_animation" not in st.session_state:
    st.session_state.active_animation = "idle"

# Initialize chatbot messages history
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Hello! I can control the 3D model. Try telling me to: 'walk', 'run', or 'stop/idle'!"}
    ]

# Mapping of animations
animation_options = {
    "idle": "Idle 💤",
    "walking": "Walking 🚶",
    "running": "Running 🏃"
}

option_keys = list(animation_options.keys())
try:
    default_idx = option_keys.index(st.session_state.active_animation)
except ValueError:
    default_idx = 0

# Sidebar selector (automatically synced)
selected_key = st.sidebar.radio(
    "Select Model Animation",
    options=option_keys,
    format_func=lambda x: animation_options[x],
    index=default_idx
)

# Update session state if sidebar changes
if selected_key != st.session_state.active_animation:
    st.session_state.active_animation = selected_key

st.sidebar.markdown("---")
st.sidebar.subheader("About the Setup")
st.sidebar.write(
    """
    - **Engine**: Three.js (WebGL)
    - **Controls**: OrbitControls (Left Click to Rotate, Right Click to Pan, Scroll to Zoom)
    - **Model**: Khronos Group Fox (GLTF/GLB)
    - **Transition**: Smooth Linear Interpolated Cross-Fade (`fadeToAction`)
    """
)

# Main UI layout
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Interactive 3D Canvas")
    # Render the component passing the selected animation name
    render_threejs_viewer(st.session_state.active_animation)

with col2:
    st.subheader("AI Mascot Assistant")
    
    # Chat container with fixed height for premium feel
    chat_container = st.container(height=350)
    with chat_container:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
    # Chat Input
    if prompt := st.chat_input("Command the mascot (e.g. 'start running', 'walk slower', 'please stand still')..."):
        # Display user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Simple rule-based processing for fast local response (or LLM call)
        prompt_lower = prompt.lower()
        if "run" in prompt_lower or "running" in prompt_lower or "fast" in prompt_lower:
            st.session_state.active_animation = "running"
            response = "Understood! Making the mascot run. 🏃"
        elif "walk" in prompt_lower or "walking" in prompt_lower or "slow" in prompt_lower:
            st.session_state.active_animation = "walking"
            response = "Sure, the mascot is now walking. 🚶"
        elif any(word in prompt_lower for word in ["stop", "idle", "stand", "still", "stay", "rest", "sleep"]):
            st.session_state.active_animation = "idle"
            response = "Mascot is now standing idle. 💤"
        else:
            response = f"I received your command: '{prompt}'. However, I only support the commands: 'walk', 'run', and 'idle/stop'. Please try one of those!"

        # Add assistant response and force rerun to update Three.js rendering
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()

