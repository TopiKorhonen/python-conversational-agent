import json
import urllib.request

import streamlit as st
from python_conversational_agent.chat_agent.chat_agent import ChatAgent


@st.cache_data(show_spinner=False)
def get_ollama_models(base_url: str = "http://localhost:11434"):
    try:
        with urllib.request.urlopen(f"{base_url}/api/tags", timeout=10) as response:
            data = json.load(response)

        names = []
        for model in data.get("models", []):
            name = model.get("name") or model.get("model")
            if name:
                names.append(name)

        return sorted(set(names))
    except Exception:
        return []


st.set_page_config(
    page_title="Python Conversational Agent",
    layout="centered",
)

st.title("Python-Based Conversational Agent", text_alignment="center")

models = get_ollama_models()

if not models:
    models = ["mistral:latest"]

st.sidebar.caption("Start Ollama first with: ollama serve")
selected_model = st.sidebar.selectbox(
    "Choose Ollama model",
    options=models,
    index=0,
)

if "agent" not in st.session_state or st.session_state.agent.model != selected_model:
    st.session_state.agent = ChatAgent(model=selected_model)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    response = st.session_state.agent.generate_response(user_input)

    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)