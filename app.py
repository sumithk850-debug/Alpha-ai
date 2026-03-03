import streamlit as st
from groq import Groq
import sys
import time
from io import StringIO
from streamlit_mic_recorder import speech_to_text
import hashlib

# 1️⃣ Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ DeepSeek Edition", page_icon="🧠", layout="wide")

# 2️⃣ User Authentication & State Logic
if "user_db" not in st.session_state:
    st.session_state.user_db = {}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3️⃣ Custom UI Styling
st.markdown("""
<style>
    .premium-banner { width:100%; padding:12px; background-color:#FFD700; color:#000; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:20px; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 50px; font-weight: bold; transition:0.3s; }
    .thinking-box { padding: 15px; background-color: #1a1a1a; border-left: 5px solid #00ffcc; color: #00ffcc; font-family: 'Courier New', monospace; margin-bottom: 10px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# 4️⃣ Login UI (Simplified for brevity)
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ Security</h1>', unsafe_allow_html=True)
    user = st.text_input("Username")
    pas = st.text_input("Password", type="password")
    if st.button("Access Alpha"):
        if user == "hasith123": # Admin bypass
            st.session_state.logged_in = True
            st.session_state.current_user = "Hasith"
            st.rerun()
        else: st.error("Invalid credentials")
    st.stop()

# 5️⃣ Groq API Setup (Using DeepSeek-R1)
# Make sure GROQ_API_KEY is in your st.secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 6️⃣ Sidebar
with st.sidebar:
    st.title("⚙️ Alpha Control")
    st.write(f"Active User: **{st.session_state.current_user}**")
    st.info("Model: DeepSeek-R1 (Distill Llama 70B)")
    temp = st.slider("Reasoning Creativity:", 0.0, 1.5, 0.6)
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# 7️⃣ Main Interface
st.markdown(f'<div class="premium-banner">⚡ Powered by DeepSeek-R1 (via Groq)</div>', unsafe_allow_html=True)

# History Display
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input Handling
v_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='voice_v1')
u_input = st.chat_input("Ask Alpha's DeepSeek brain...")
final_q = v_text if v_text else u_input

if final_q:
    st.session_state.messages.append({"role": "user", "content": final_q})
    st.rerun()

# 8️⃣ DeepSeek Reasoning + Streaming Logic
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        response_placeholder = st.empty()
        
        # Thinking Phase
        thinking_placeholder.markdown('<div class="thinking-box">Alpha\'s pro thinking (DeepSeek-R1) ... 🧠</div>', unsafe_allow_html=True)
        
        try:
            # Groq Chat Completion with Streaming
            completion = client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[
                    {"role": "system", "content": "You are Alpha AI. Always reply in the same language the user uses. Be logical and direct."},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                temperature=temp,
                stream=True,
                stop=None,
            )

            full_res = ""
            thinking_placeholder.empty()
            
            # Simple stop mechanism using a checkbox
            stop_btn = st.checkbox("⏹️ Stop Alpha")

            for chunk in completion:
                if stop_btn:
                    full_res += "\n\n*[Stopped]*"
                    break
                
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    # Typewriter effect
                    for char in content:
                        full_res += char
                        response_placeholder.markdown(full_res + "▌")
                        time.sleep(0.002) # DeepSeek is fast, so typing is fast!
            
            response_placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"DeepSeek Error: {e}")
