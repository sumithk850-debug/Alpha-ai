import streamlit as st
from groq import Groq
import sys
from io import StringIO
import base64

# ---------------------------------------------------------
# 1. Page Configuration & Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="Alpha AI: Friendly Assistant & Python Runner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Session States
if "messages" not in st.session_state:
    st.session_state.messages = []
if "python_output" not in st.session_state:
    st.session_state.python_output = ""

# 🛡️ API Setup - Replace with your actual secret key
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("GROQ_API_KEY not found in Streamlit Secrets! Check your secrets configuration.")
    st.stop()

# ---------------------------------------------------------
# 2. Modern UI Styling (Dark Theme)
# ---------------------------------------------------------
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    
    /* Center header with Hasith's branding */
    .hasith-branding {
        text-align: center;
        margin-bottom: 0px;
        padding-top: 1rem;
    }
    .hasith-title {
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
        font-size: 50px;
        font-weight: 800;
        margin: 0px;
    }
    .hasith-tagline {
        color: #a0a0a0;
        font-size: 16px;
        margin-top: -10px;
        margin-bottom: 25px;
    }

    /* Style for buttons to be modern & golden */
    div.stButton > button {
        background-color: #1a1e26;
        color: #FFD700 !important;
        border: 1px solid #30363d;
        border-radius: 12px;
        width: 100%;
        transition: 0.3s;
        font-weight: bold;
    }
    div.stButton > button:hover {
        border-color: #FFD700;
        background-color: #252a35;
    }
    div.stButton > button:active {
        background-color: #FFD700;
        color: #0e1117 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. Sidebar - Control Panel & Python Lab
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Control Panel")
    ai_mode = st.radio("AI Focus Mode:", ["Normal Assistant", "Python Deep Dive Expert"], index=1)
    
    st.markdown("---")
    st.markdown("### 🛠️ Response Tuning")
    # Response precision, variety and length penalties
    temp_val = st.slider("Response Precision (Temp):", 0.0, 1.0, 0.5)
    presence_pen = st.slider("Diversity Penalty (AI Model):", 0.0, 2.0, 1.3)
    freq_pen = st.slider("Repetition Penalty (AI Model):", 0.0, 2.0, 1.3)
    
    st.markdown("---")
    st.markdown("### 🗑️ Memory Management")
    if st.button("Wipe All Chat Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 🐍 Python Interpreter")
    py_code = st.text_area("Write Python code here...", height=150)
    if st.button("🚀 Run Python"):
        buffer = StringIO()
        sys.stdout = buffer
        try:
            exec(py_code)
            output = buffer.getvalue()
            st.session_state.python_output = output
        except Exception as e:
            st.session_state.python_output = f"Error: {e}"
        finally:
            sys.stdout = sys.__stdout__
    
    if st.session_state.python_output:
        st.markdown("**Python Output:**")
        st.code(st.session_state.python_output, language="text")

# ---------------------------------------------------------
# 4. Main Interface - Header & Quick Actions
# ---------------------------------------------------------
# Branding Area
st.markdown(
    '<div class="hasith-branding"><h1 class="hasith-title">Alpha AI <span style="color:#FFD700;">⚡</span></h1>'
    '<p class="hasith-tagline">Friendly AI Assistant & Python Code Runner | Developed by Hasith</p></div>',
    unsafe_allow_html=True
)

# Quick Action Buttons
col1, col2, col3 = st.columns(3)

if col1.button("📝 Summarize (discussion)"):
    st.session_state.messages.append({"role": "user", "content": "Please summarize our entire discussion."})
    st.rerun()
if col2.button("💡 Deep Dive (topic)"):
    st.session_state.messages.append({"role": "user", "content": "Can you deep dive into this topic for me?"})
    st.rerun()
if col3.button("✅ Refine (text/code)"):
    st.session_state.messages.append({"role": "user", "content": "Improve and refine my previous response or code."})
    st.rerun()

st.write("---")

# ---------------------------------------------------------
# 5. Main AI Conversational Engine
# ---------------------------------------------------------
# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
user_input = st.chat_input("Ask Alpha something...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Assistant Response
    with st.chat_message("assistant"):
        thinking_text = "Brain Ultra Thinking..." if ai_mode == "Python Deep Dive Expert" else "Thinking... ⚡"
        with st.spinner(thinking_text):
            # Groq connection
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are Alpha AI by Hasith. Respond with professional expertise. Focus mode is {ai_mode}. Temperature is {temp_val}. Presence Penalty is {presence_pen}. Frequency Penalty is {freq_pen}."}
                ] + st.session_state.messages[-10:],
                temperature=temp_val,
                presence_penalty=presence_pen,
                frequency_penalty=freq_pen,
                stream=True,
            )
            
            # Stream response
            response_container = st.empty()
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_container.markdown(full_response + "▌")
            
            # Final output and save message
            response_container.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun()
