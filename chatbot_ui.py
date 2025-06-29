import os
import streamlit as st
import requests
import json
from dotenv import load_dotenv
load_dotenv()

# ✅ Wide layout for full-width interface
st.set_page_config(page_title="Developer Assistant", layout="wide")

# ✅ Load external CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# ✅ Page header
with st.container():
    st.markdown("<h1 class='chat-title'>💬 Developer Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p class='chat-subtitle'>Ask anything about developers, domains, and contributors.</p>", unsafe_allow_html=True)

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL")

# ✅ Store conversation in session
if "messages" not in st.session_state:
    st.session_state.messages = []

# ✅ Backend call
def get_response_from_backend(user_message):
    try:
        response = requests.post(API_GATEWAY_URL, json={"message": user_message})
        if response.status_code == 200:
            outer_json = response.json()
            body_json = json.loads(outer_json.get("body", "{}"))
            return body_json.get("response", "No response found in body.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Request failed: {e}"

# ✅ Display messages with labels
for msg in st.session_state.messages:
    role = msg["role"]
    label = "You" if role == "user" else "Assistant"
    css_class = "user" if role == "user" else "assistant"

    with st.chat_message(role):
        st.markdown(f"<div class='chat-label'>{label}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-message {css_class}'>{msg['text']}</div>", unsafe_allow_html=True)

# ✅ Chat input
if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "text": prompt})
    with st.chat_message("user"):
        st.markdown("<div class='chat-label'>You</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-message user'>{prompt}</div>", unsafe_allow_html=True)

    with st.spinner("Thinking..."):
        reply = get_response_from_backend(prompt)

    st.session_state.messages.append({"role": "assistant", "text": reply})
    with st.chat_message("assistant"):
        st.markdown("<div class='chat-label'>Assistant</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-message assistant'>{reply}</div>", unsafe_allow_html=True)
