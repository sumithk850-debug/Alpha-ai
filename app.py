import streamlit as st
import google.generativeai as genai
import sys
import time
from io import StringIO
from streamlit_mic_recorder import speech_to_text
import hashlib

# 1️⃣ Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Ultimate", page_icon="⚡", layout="wide")

# 2️⃣ User Authentication & State Logic
if "user_db" not in st.session_state:
    st.session_state.user_db = {}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.is_admin = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3️⃣ Custom UI Styling
st.markdown("""
<style>
    .premium-banner { width:100%; padding:12px; background-color:#FFD700; color:#000; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:20px; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 50px; font-weight: bold; transition:0.3s; }
    div.stButton > button:hover { border-color:#FFD700; background-color:#252525; }
    .thinking-box { padding: 10px; background-color: #262730; border-left: 5px solid #FFD700; color: #FFD700; font-style: italic; margin-bottom: 10px; border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

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

# 5️⃣ Gemini API Setup (GitHub Secrets හරහා ලබා ගනී)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("API Key not found! Please add GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

# 6️⃣ Sidebar
with st.sidebar:
    st.title("⚙️ Alpha Control Panel")
    st.write(f"User: **{st.session_state.current_user}**")
    temp = st.slider("Logic Precision:", 0.0, 2.0, 1.0)
    
    st.write("---")
    if not st.session_state.is_admin:
        rem = 1500 - st.session_state.user_db[st.session_state.current_user]["msg_count"]
        st.write(f"Chats Left: **{rem}**")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# 7️⃣ Main Interface
st.markdown(f'<div class="premium-banner">⚡ Welcome {st.session_state.current_user}</div>', unsafe_allow_html=True)
st.markdown('<h1 style="text-align:center;">Alpha AI ⚡</h1>', unsafe_allow_html=True)

# Display Chat History
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if st.button(f"🔊 Speak", key=f"sp_{i}"): speak_text(msg["content"])

# Input Handling
v_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='voice_v5')
u_input = st.chat_input("Ask Alpha anything...")
final_q = v_text if v_text else u_input

if final_q:
    if not st.session_state.is_admin:
        st.session_state.user_db[st.session_state.current_user]["msg_count"] += 1
    st.session_state.messages.append({"role": "user", "content": final_q})
    st.rerun()

# 8️⃣ Alpha's Thinking & Response Logic
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        response_placeholder = st.empty()
        
        # Display Alpha's Pro Thinking
        thinking_placeholder.markdown('<div class="thinking-box">Alpha\'s pro thinking... 🧠</div>', unsafe_allow_html=True)
        
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-lite",
                system_instruction="You are Alpha AI by Hasith. Reply in the same language used by the user."
            )
            
            # Convert History for Gemini
            history = []
            for m in st.session_state.messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                history.append({"role": role, "parts": [m["content"]]})
            
            chat = model.start_chat(history=history)
            
            # Start Streaming Response
            full_res = ""
            stop_btn = st.checkbox("⏹️ Stop Alpha") # Generation නවත්වන බොත්තම
            
            response_stream = chat.send_message(
                st.session_state.messages[-1]["content"],
                generation_config=genai.types.GenerationConfig(temperature=temp),
                stream=True
            )

            thinking_placeholder.empty() # Remove thinking box when starting to type

            for chunk in response_stream:
                if stop_btn:
                    full_res += "\n\n*[Alpha was stopped]*"
                    break
                
                chunk_text = chunk.text
                for char in chunk_text:
                    full_res += char
                    response_placeholder.markdown(full_res + "▌")
                    time.sleep(0.008) # Typing effect speed
            
            response_placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"Alpha encountered an error: {e}")
