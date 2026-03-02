import streamlit as st
from groq import Groq
import numpy as np
import json
from datetime import datetime

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Alpha AI ⚡", layout="wide")

# ==============================
# SESSION MEMORY ONLY (No DB)
# ==============================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================
# HEADER
# ==============================
st.title("Alpha AI ⚡")
st.caption("Completely Free – No Login Required")

# ==============================
# AI ENGINE
# ==============================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("GROQ_API_KEY missing in Streamlit Secrets!")
    st.stop()

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask Alpha AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages[-15:],
                stream=True
            )
            response = st.write_stream(stream)
            if not isinstance(response, str):
                response = str(response)
        except Exception as e:
            response = f"AI Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": response})

# ==============================
# QUICK PYTHON RUNNER (Optional)
# ==============================
st.sidebar.subheader("🐍 Python Lab (Optional)")
py_code = st.sidebar.text_area("Write Python code here", height=150)
if st.sidebar.button("Run Code"):
    import sys, io
    buffer = io.StringIO()
    sys.stdout = buffer
    try:
        exec(py_code)
        st.sidebar.code(buffer.getvalue() if buffer.getvalue() else "Done.", language="text")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
    finally:
        sys.stdout = sys.__stdout__
