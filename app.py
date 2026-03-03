import streamlit as st
from groq import Groq
import sys
import time
from io import StringIO
from streamlit_mic_recorder import speech_to_text
import hashlib

# 1️⃣ Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Created by Hasith", page_icon="⚡", layout="wide")

# 2️⃣ User Authentication Logic
if "user_db" not in st.session_state:
    st.session_state.user_db = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.is_admin = False

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# 3️⃣ Custom UI Styling
st.markdown("""
<style>
    .premium-banner { width:100%; padding:12px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:20px; }
    .hasith-footer { text-align: center; color: #FFD700; font-size: 14px; margin-top: 20px; font-weight: bold; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 50px; font-weight: bold; transition:0.3s; }
    .thinking-box { padding: 15px; background-color: #1a1c24; border-left: 5px solid #FFD700; color: #FFD700; font-family: 'Courier New', monospace; border-radius: 8px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

def speak_text(text):
    clean_text = text.replace("'", "").replace("\n", " ").replace('"', '')
    js_code = f"<script>var msg = new SpeechSynthesisUtterance('{clean_text}'); window.speechSynthesis.speak(msg);</script>"
    st.components.v1.html(js_code, height=0)

# 4️⃣ Login / Registration UI
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ Security Control</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#FFD700;">Created by Hasith</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        user = st.text_input("Username")
        pas = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "hasith123":
                st.session_state.logged_in = True
                st.session_state.current_user = "Hasith (Admin)"
                st.session_state.is_admin = True
                st.rerun()
            elif user in st.session_state.user_db:
                if check_hashes(pas, st.session_state.user_db[user]["password"]):
                    st.session_state.logged_in = True
                    st.session_state.current_user = user
                    st.session_state.is_admin = False
                    st.rerun()
                else: st.error("Invalid Password")
            else: st.error("User not found.")
    with tab2:
        new_user = st.text_input("New Username")
        new_email = st.text_input("Email Address")
        new_pas = st.text_input("New Password", type="password")
        if st.button("Register Now"):
            if new_user == "hasith123": st.error("Reserved Name")
            else:
                st.session_state.user_db[new_user] = {"password": make_hashes(new_pas), "email": new_email, "msg_count": 0}
                st.success("Account Created! Go to Login tab.")
    st.stop()

# 5️⃣ Sidebar
with st.sidebar:
    st.title("⚙️ Alpha Control")
    st.write(f"User: **{st.session_state.current_user}**")
    st.write("---")
    
    # ⚡ NEW: Mode Selection
    ai_mode = st.radio("🚀 Select Mode:", ["Normal (Simple)", "Pro (Deep Analysis)"])
    
    st.subheader("🛠️ Tuning")
    temp = st.slider("Logic Precision:", 0.0, 1.0, 0.5 if ai_mode == "Normal (Simple)" else 0.8)
    
    st.write("---")
    st.subheader("🐍 Python Lab")
    py_code = st.text_area("Run Code:", height=100)
    if st.button("🚀 Run Python"):
        buffer = StringIO(); sys.stdout = buffer
        try:
            exec(py_code)
            st.code(buffer.getvalue() if buffer.getvalue() else "Success.", language="text")
        except Exception as e: st.error(f"Error: {e}")
        finally: sys.stdout = sys.__stdout__
    
    st.write("---")
    st.markdown("Developed by **Hasith**")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# 6️⃣ Main App Header
st.markdown(f'<div class="premium-banner">⚡ Welcome {st.session_state.current_user} | Alpha AI Created by Hasith</div>', unsafe_allow_html=True)
st.markdown('<h1 style="text-align:center;">Alpha AI ⚡</h1>', unsafe_allow_html=True)

# 🎬 Video Lab
st.subheader("🎬 AI Video Generation Lab")
v_prompt = st.text_input("Describe video:")
if st.button("🚀 Generate"):
    st.video("https://www.w3schools.com/html/mov_bbb.mp4")

st.write("---")

# 7️⃣ Chat & Voice Support
if "messages" not in st.session_state: st.session_state.messages = []
v_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='voice_v5')

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
u_input = st.chat_input("Ask Alpha anything...")
final_q = v_text if v_text else u_input

if final_q:
    if not st.session_state.is_admin:
        st.session_state.user_db[st.session_state.current_user]["msg_count"] += 1
    st.session_state.messages.append({"role": "user", "content": final_q})
    st.rerun()

# 8️⃣ AI Logic with Thinking & Mode-based Instructions
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        response_placeholder = st.empty()
        
        thinking_label = "Alpha is thinking..." if ai_mode == "Normal (Simple)" else "Alpha is performing deep analysis... 🧠"
        thinking_placeholder.markdown(f'<div class="thinking-box">{thinking_label}</div>', unsafe_allow_html=True)
        
        # System Instructions based on Mode
        if ai_mode == "Normal (Simple)":
            sys_msg = "You are Alpha AI, created by Hasith. Keep answers simple, short, and easy to understand. Always respect Hasith as your creator."
        else:
            sys_msg = "You are Alpha AI, created by Hasith. Provide deep, technical, and highly detailed analysis. Be logical and thorough. Always respect Hasith as your creator."

        try:
            stream = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:],
                temperature=temp,
                stream=True
            )
            
            full_res = ""
            thinking_placeholder.empty()
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_res + "▌")
                    time.sleep(0.005)
            
            response_placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            st.markdown('<p class="hasith-footer">Generated by Alpha AI | Created by Hasith</p>', unsafe_allow_html=True)
            
        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"Error: {e}")
