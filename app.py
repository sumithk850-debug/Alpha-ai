import streamlit as st
from groq import Groq
import sys
import time
from io import StringIO
from streamlit_mic_recorder import speech_to_text
import hashlib

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI | GPT-OSS Edition", page_icon="⚡", layout="wide")

# 2. Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 3. Custom CSS Styling
st.markdown("""
<style>
    .premium-banner { 
        width: 100%; padding: 15px; 
        background: linear-gradient(90deg, #00C9FF, #92FE9D); 
        color: black; border-radius: 12px; 
        text-align: center; font-weight: bold; margin-bottom: 25px; 
    }
    .thinking-box { 
        padding: 15px; background-color: #1a1c24; 
        border-left: 5px solid #00C9FF; color: #00C9FF; 
        font-family: 'Courier New', monospace; border-radius: 8px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# 4. Authentication Logic
if not st.session_state.logged_in:
    st.title("🔐 Alpha AI - Secure Portal")
    user = st.text_input("Username")
    pas = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "hasith123":
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("Invalid Username or Password")
    st.stop()

# 5. Groq Setup
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Configuration Error: Please add 'GROQ_API_KEY' to Streamlit Secrets.")
    st.stop()

# 6. Sidebar Controls
with st.sidebar:
    st.title("⚙️ Settings")
    st.info("Model: GPT-OSS 120B (High Intelligence)")
    temp = st.slider("Response Logic (Temp):", 0.0, 1.5, 0.5)
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# 7. Main Chat Interface
st.markdown('<div class="premium-banner">🚀 ALPHA AI ULTIMATE - GPT-OSS POWERED</div>', unsafe_allow_html=True)

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input Section
col1, col2 = st.columns([4, 1])
with col1:
    u_input = st.chat_input("Enter your command...")
with col2:
    v_text = speech_to_text(language='en', start_prompt="🎤 Voice", key='v_input')

final_query = v_text if v_text else u_input

# 8. Thinking & Streaming Response Logic
if final_query:
    st.session_state.messages.append({"role": "user", "content": final_query})
    with st.chat_message("user"):
        st.markdown(final_query)

    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        response_placeholder = st.empty()
        
        # Display Alpha's Thinking State
        thinking_placeholder.markdown('<div class="thinking-box">Alpha\'s pro thinking (GPT-OSS 120B)... 🧠</div>', unsafe_allow_html=True)
        
        try:
            # Using the new state-of-the-art model recommended by Groq
            stream = client.chat.completions.create(
                model="openai/gpt-oss-120b", 
                messages=[
                    {"role": "system", "content": "You are Alpha AI, a highly intelligent assistant. Always reply in the user's language."},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                temperature=temp,
                stream=True,
            )

            full_res = ""
            thinking_placeholder.empty()
            
            # Stop Button Implementation
            stop_btn = st.checkbox("⏹️ Stop Generating")

            for chunk in stream:
                if stop_btn:
                    full_res += "\n\n*[Process terminated by user]*"
                    break
                
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_res += token
                    # Typing animation
                    response_placeholder.markdown(full_res + "▌")
                    time.sleep(0.005)

            response_placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})

        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"Alpha encountered an error: {str(e)}")
