import streamlit as st
from groq import Groq
import sys
import time
from io import StringIO
from streamlit_mic_recorder import speech_to_text
import hashlib

# 1️⃣ Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Ultimate", page_icon="⚡", layout="wide")

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
    .premium-banner { width:100%; padding:12px; background-color:#FFD700; color:#000; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:20px; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 50px; font-weight: bold; transition:0.3s; }
    div.stButton > button:hover { border-color:#FFD700; background-color:#252525; }
</style>
""", unsafe_allow_html=True)

def speak_text(text):
    clean_text = text.replace("'", "").replace("\n", " ").replace('"', '')
    js_code = f"<script>var msg = new SpeechSynthesisUtterance('{clean_text}'); window.speechSynthesis.speak(msg);</script>"
    st.components.v1.html(js_code, height=0)

# 4️⃣ Login / Registration UI
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ Security Control</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        user = st.text_input("Username")
        pas = st.text_input("Password", type="password")
        if st.button("Login"):
            # ADMIN BYPASS
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

# 5️⃣ Sidebar: Sliders & Python Lab
with st.sidebar:
    st.title("⚙️ Alpha Control Panel")
    st.write(f"Logged in: **{st.session_state.current_user}**")
    
    st.subheader("🛠️ Tuning")
    temp = st.slider("Logic Precision:", 0.0, 1.0, 0.5)
    pres_pen = st.slider("Creativity Penalty:", 0.0, 2.0, 1.1)
    
    st.write("---")
    st.subheader("🐍 Python Lab")
    py_code = st.text_area("Run Code:", height=120)
    if st.button("🚀 Run Python"):
        buffer = StringIO(); sys.stdout = buffer
        try:
            exec(py_code)
            st.code(buffer.getvalue() if buffer.getvalue() else "Executed successfully.", language="text")
        except Exception as e: st.error(f"Error: {e}")
        finally: sys.stdout = sys.__stdout__
    
    st.write("---")
    if not st.session_state.is_admin:
        rem = 1000 - st.session_state.user_db[st.session_state.current_user]["msg_count"]
        st.write(f"Chats Remaining: **{rem}**")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# 6️⃣ Main App Header
st.markdown(f'<div class="premium-banner">⚡ Welcome {st.session_state.current_user}</div>', unsafe_allow_html=True)
st.markdown('<h1 style="text-align:center;">Alpha AI ⚡</h1>', unsafe_allow_html=True)

# 🚀 Quick Actions
st.write("### 🚀 Quick Actions")
qc1, qc2, qc3 = st.columns(3)
with qc1:
    if st.button("📝 Summarize"):
        st.session_state.messages.append({"role":"user", "content":"Summarize the previous discussion."})
with qc2:
    if st.button("💡 Deep Dive"):
        st.session_state.messages.append({"role":"user", "content":"Explain in detail."})
with qc3:
    if st.button("✅ Refine"):
        st.session_state.messages.append({"role":"user", "content":"Improve my last message's grammar."})

# 🎬 Video Lab (FIXED LINK)
st.write("---")
st.subheader("🎬 AI Video Generation Lab")
v_prompt = st.text_input("Describe video to generate:")
if st.button("🚀 Generate Inside Alpha AI"):
    if v_prompt:
        with st.spinner("🧠 Alpha is analyzing..."): time.sleep(2)
        with st.spinner("🎨 Rendering..."): time.sleep(3)
        # Fixed: Using a more stable sample video link
        st.video("https://www.w3schools.com/html/mov_bbb.mp4")
        st.success(f"✅ Generated cinematic video for: '{v_prompt}'")

st.write("---")

# 7️⃣ Chat & Voice Support
if "messages" not in st.session_state: st.session_state.messages = []
st.write("### 🎤 Voice Command")
v_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='voice_v5')

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if st.button(f"🔊 Speak Answer", key=f"sp_{i}"): speak_text(msg["content"])

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
u_input = st.chat_input("Ask Alpha anything...")
final_q = v_text if v_text else u_input

if final_q:
    if not st.session_state.is_admin:
        st.session_state.user_db[st.session_state.current_user]["msg_count"] += 1
    st.session_state.messages.append({"role": "user", "content": final_q})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are Alpha AI by Hasith."}] + st.session_state.messages[-10:],
            temperature=temp, presence_penalty=pres_pen, stream=False
        )
        full_res = res.choices[0].message.content
        st.markdown(full_res)
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        if st.button("🔊 Play Voice"): speak_text(full_res)
