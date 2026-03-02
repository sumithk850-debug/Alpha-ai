import streamlit as st
from groq import Groq
import sys
from io import StringIO
from streamlit_mic_recorder import speech_to_text
import hashlib

# 1️⃣ Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Secure", page_icon="⚡", layout="wide")

# 2️⃣ User Authentication & Database
if "user_db" not in st.session_state:
    st.session_state.user_db = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# 3️⃣ Custom UI Styling
st.markdown("""
<style>
    .premium-banner { width:100%; padding:12px; background-color:#FFD700; color:#000; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:20px; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 50px; font-weight: bold; transition:0.3s; }
    div.stButton > button:hover { border-color:#FFD700; background-color:#252525; transform: translateY(-2px); }
    .action-button > div > button { height: 80px !important; background: rgba(30, 41, 59, 0.5) !important; border: 1px solid #1e293b !important; }
</style>
""", unsafe_allow_html=True)

def speak_text(text):
    clean_text = text.replace("'", "").replace("\n", " ").replace('"', '')
    js_code = f"<script>var msg = new SpeechSynthesisUtterance('{clean_text}'); window.speechSynthesis.speak(msg);</script>"
    st.components.v1.html(js_code, height=0)

# 4️⃣ Login / Registration Logic
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ Access Control</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        user = st.text_input("Username")
        pas = st.text_input("Password", type="password")
        if st.button("Login"):
            # ✅ HASITH123 ADMIN BYPASS
            if user == "hasith123":
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
                st.error("User not found. Please Register.")
    with tab2:
        new_user = st.text_input("New Username")
        new_email = st.text_input("Email Address")
        new_pas = st.text_input("New Password", type="password")
        if st.button("Create My Account"):
            if new_user == "hasith123": st.error("Reserved Name")
            else:
                st.session_state.user_db[new_user] = {"password": make_hashes(new_pas), "email": new_email}
                st.success("Account Created! Use Login tab.")
    st.stop()

# 5️⃣ Main Interface (Logged In)
st.markdown(f'<div class="premium-banner">⚡ Welcome, {st.session_state.current_user} | Alpha AI Premium Interface</div>', unsafe_allow_html=True)

# --- Sidebar: Sliders & Python Lab ---
with st.sidebar:
    st.title("⚙️ System Tuning")
    st.write(f"Logged in: **{st.session_state.current_user}**")
    
    st.subheader("🛠️ Intelligence Logic")
    temp = st.slider("Logic Precision (Temp):", 0.0, 1.0, 0.5)
    pres_pen = st.slider("Creativity Penalty:", 0.0, 2.0, 1.2)
    
    st.write("---")
    st.subheader("🐍 Python Lab")
    py_code = st.text_area("Run Python:", height=120)
    if st.button("🚀 Run Code"):
        buffer = StringIO(); sys.stdout = buffer
        try:
            exec(py_code)
            st.code(buffer.getvalue() if buffer.getvalue() else "Success.", language="text")
        except Exception as e: st.error(f"Error: {e}")
        finally: sys.stdout = sys.__stdout__
    
    st.write("---")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- Main App Header ---
st.markdown('<h1 style="text-align:center; font-size: 50px;">Alpha AI ⚡</h1>', unsafe_allow_html=True)

# 🎤 Voice Input
st.write("### 🎤 Voice Command")
voice_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='v_input')

# 🚀 Quick Actions Section
st.write("### 🚀 Quick Actions")
qc1, qc2, qc3 = st.columns(3)
with qc1:
    if st.button("📝 Summarize\nShort Summary", key="q1"):
        st.session_state.messages.append({"role":"user", "content":"Summarize the previous context concisely."})
with qc2:
    if st.button("💡 Deep Dive\nDetailed Analysis", key="q2"):
        st.session_state.messages.append({"role":"user", "content":"Explain the previous topic in extreme detail."})
with qc3:
    if st.button("✅ Refine\nImprove Text", key="q3"):
        st.session_state.messages.append({"role":"user", "content":"Refine and polish the grammar of my last message."})

st.write("---")

# --- Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if st.button(f"🔊 Speak Answer", key=f"sp_{i}"):
                speak_text(msg["content"])

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
user_input = st.chat_input("Ask anything to Alpha...")

final_query = voice_text if voice_text else user_input

if final_query:
    st.session_state.messages.append({"role": "user", "content": final_query})
    st.rerun()

# AI Generation
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Alpha is thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are Alpha AI by Hasith."}] + st.session_state.messages[-10:],
                temperature=temp,
                presence_penalty=pres_pen,
                stream=False
            )
            res = response.choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            if st.button("🔊 Play Voice Now"):
                speak_text(res)
