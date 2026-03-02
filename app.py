import streamlit as st
from groq import Groq
import sys
from io import StringIO
from streamlit_mic_recorder import speech_to_text
import hashlib

# -------------------------
# 1️⃣ Page Configuration
# -------------------------
st.set_page_config(page_title="Alpha AI ⚡ Secure", page_icon="⚡", layout="centered")

# -------------------------
# 2️⃣ User Authentication Logic
# -------------------------
if "user_db" not in st.session_state:
    # Default Admin (Hasith) stored
    st.session_state.user_db = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# -------------------------
# 3️⃣ Custom CSS & Voice JS
# -------------------------
st.markdown("""
<style>
    .premium-banner { width:100%; padding:10px; background-color:#FFD700; color:#000; border-radius:10px; text-align:center; font-weight:bold; margin-bottom:15px; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; transition:0.3s; font-weight: bold; }
    div.stButton > button:hover { border-color:#FFD700; background-color:#252525; }
    .stChatInputContainer { border-radius: 20px; }
</style>
""", unsafe_allow_html=True)

def speak_text(text):
    clean_text = text.replace("'", "").replace("\n", " ").replace('"', '')
    js_code = f"<script>var msg = new SpeechSynthesisUtterance('{clean_text}'); window.speechSynthesis.speak(msg);</script>"
    st.components.v1.html(js_code, height=0)

# -------------------------
# 4️⃣ Login / Registration UI
# -------------------------
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ Access</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        user = st.text_input("Username")
        pas = st.text_input("Password", type="password")
        if st.button("Login"):
            # ✅ HASITH ADMIN BYPASS (No password needed for you)
            if user.lower() == "hasith":
                st.session_state.logged_in = True
                st.session_state.current_user = "Hasith (Admin)"
                st.rerun()
            elif user in st.session_state.user_db:
                if check_hashes(pas, st.session_state.user_db[user]["password"]):
                    st.session_state.logged_in = True
                    st.session_state.current_user = user
                    st.rerun()
                else:
                    st.error("Invalid Password")
            else:
                st.error("User not found")

    with tab2:
        new_user = st.text_input("New Username")
        new_email = st.text_input("Email Address")
        new_pas = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            if new_user.lower() == "hasith":
                st.error("Admin name reserved")
            else:
                st.session_state.user_db[new_user] = {
                    "password": make_hashes(new_pas),
                    "email": new_email
                }
                st.success("Account created! Please Login.")
    st.stop()

# -------------------------
# 5️⃣ Main App (After Login)
# -------------------------
st.markdown(f'<div class="premium-banner">Logged in as: {st.session_state.current_user}</div>', unsafe_allow_html=True)
st.markdown('<h1 style="text-align:center;">Alpha AI ⚡</h1>', unsafe_allow_html=True)

# Voice Input Section
st.write("### 🎤 Voice Command")
voice_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='st_voice')

# Sidebar Tools
with st.sidebar:
    st.title("⚙️ Controls")
    st.write(f"User: {st.session_state.current_user}")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    st.write("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# AI Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
user_input = st.chat_input("Type your message...")

final_query = voice_text if voice_text else user_input

if final_query:
    st.session_state.messages.append({"role": "user", "content": final_query})

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if st.button(f"🔊 Speak", key=f"sp_{i}"):
                speak_text(msg["content"])

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Alpha is thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are Alpha AI by Hasith."}] + st.session_state.messages[-10:],
                stream=False
            )
            res = response.choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            if st.button("🔊 Play Voice"):
                speak_text(res)
