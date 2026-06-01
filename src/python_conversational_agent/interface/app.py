import streamlit as st
from python_conversational_agent.chat_agent.chat_agent import ChatAgent

st.set_page_config(
    page_title="Python Conversational Agent",
    layout="centered"
)

st.title("Python-Based Conversational Agent", text_alignment="center")

if "agent" not in st.session_state:
    st.session_state.agent = ChatAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)
    
    response = st.session_state.agent.generate_response(user_input)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):
        st.markdown(response)
