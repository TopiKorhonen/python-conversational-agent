from __future__ import annotations

import streamlit as st

from agent import AgentContext, LMStudioAgent
from agent.lmstudio_client import LMStudioUnavailableError


st.set_page_config(page_title="LM Studio Mascot Agent", page_icon="🤖")
st.title("LM Studio Mascot Agent Demo")
st.caption("Text-only test page for the LLM gateway layer.")


@st.cache_resource
def get_agent() -> LMStudioAgent:
    return LMStudioAgent()


try:
    agent = get_agent()
except LMStudioUnavailableError as exc:
    st.error(str(exc))
    st.stop()

st.sidebar.write("Model")
st.sidebar.code(agent.model)

user_mood = st.sidebar.selectbox(
    "Simulated user mood",
    ["neutral", "happy", "sad", "angry", "confused", "curious"],
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.sidebar.button("Reset conversation"):
    agent.reset_history()
    st.session_state.messages = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant":
            st.caption(
                f"Expression: {message.get('expression')} | "
                f"Tone: {message.get('tone')} | "
                f"Safety: {message.get('safety')}"
            )

prompt = st.chat_input("Type a message to the mascot...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    result = agent.ask(
        prompt,
        context=AgentContext(
            user_mood=user_mood,
            interaction_mode="streamlit text demo",
            extra_context="The app is currently testing only the LM Studio gateway.",
        ),
    )

    assistant_message = {
        "role": "assistant",
        "content": result.reply,
        "expression": result.expression,
        "tone": result.tone,
        "safety": result.safety,
    }
    st.session_state.messages.append(assistant_message)

    with st.chat_message("assistant"):
        st.write(result.reply)
        st.caption(
            f"Expression: {result.expression} | "
            f"Tone: {result.tone} | "
            f"Safety: {result.safety}"
        )
