import streamlit as st
from groq import Groq
import time
import base64
import asyncio
import edge_tts
import os
from PyPDF2 import PdfReader

# --- 1. Page Configuration ---
st.set_page_config(page_title="KITT AI 🏎️ Created by Hasith", page_icon="🏎️", layout="wide")

# --- 2. KITT Audio & Animation Functions ---
def play_kitt_scanner():
    """Plays scanner sound and waits for it to complete."""
    sound_file = "kitt_scanner.mp3"
    if os.path.exists(sound_file):
        with open(sound_file, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
        time.sleep(1.8) # Wait for scanner sound to finish

async def kitt_speak(text):
    """Generates KITT's voice."""
    VOICE = "en-IE-ConnorNeural" 
    communicate = edge_tts.Communicate(text, VOICE)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    b64 = base64.b64encode(audio_data).decode()
    md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
    st.markdown(md, unsafe_allow_html=True)
    # Estimate speaking time to keep animation synced (approx 15 chars per second)
    wait_time = max(len(text) / 15, 2)
    return wait_time

def get_voice_box_html(is_active=True):
    """Returns the HTML for the voice box with active or paused state."""
    state = "running" if is_active else "paused"
    return f"""
        <div style="display: flex; align-items: flex-end; gap: 4px; height: 40px; background: #000; padding: 5px; border: 1px solid #444; border-radius: 4px; width: 60px;">
            <style>
                .v-bar {{ width: 12px; background: red; box-shadow: 0 0 8px red; animation: pulse 0.4s infinite alternate; animation-play-state: {state}; }}
                .v1 {{ height: 10px; animation-delay: 0.1s; }}
                .v2 {{ height: 30px; animation-delay: 0.2s; }}
                .v3 {{ height: 15px; animation-delay: 0.3s; }}
                @keyframes pulse {{ 0% {{ height: 8px; }} 100% {{ height: 35px; }} }}
            </style>
            <div class="v-bar v1"></div><div class="v-bar v2"></div><div class="v-bar v3"></div>
        </div>
    """

# --- 3. Loading Screen ---
if "loaded" not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <style>
                .loader { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 85vh; background: #000; text-align: center; }
                .k-text { font-size: 8vw; color: red; text-shadow: 0 0 15px red; font-family: monospace; }
                .s-bar { width: 280px; height: 12px; background: #222; position: relative; border-radius: 6px; overflow: hidden; border: 1px solid #444; margin-top: 20px;}
                .s-light { width: 60px; height: 100%; background: red; box-shadow: 0 0 20px red; position: absolute; animation: bounce 1.2s infinite alternate ease-in-out; }
                @keyframes bounce { 0% { left: 0%; } 100% { left: calc(100% - 60px); } }
            </style>
            <div class="loader">
                <div class="k-text">KITT INITIALIZING</div>
                <div class="s-bar"><div class="s-light"></div></div>
                <p style="color: #666; margin-top: 15px;">Authorized: Hasith</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(7)
    st.session_state.loaded = True
    st.rerun()

# --- 4. Security Portal ---
if "user_db" not in st.session_state: st.session_state.user_db = {"matheesha": "123", "sadev": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center; color:red; font-family:monospace;">KITT SECURITY</h1>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🔐 LOGIN", "📝 REGISTER", "⚡ CREATOR"])
    with t1:
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("Access"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
    with t2:
        reg_u = st.text_input("New ID")
        reg_p = st.text_input("New Pass", type="password")
        if st.button("Sign Up"): st.session_state.user_db[reg_u] = reg_p
    with t3:
        if st.button("Bypass Activation"):
            st.session_state.logged_in, st.session_state.user = True, "Hasith"
            st.rerun()
    st.stop()

# --- 5. Main Dashboard ---
st.markdown("<style>.stApp { background: #000; color: #fff; } .banner { background: linear-gradient(90deg, #900, #f00); padding: 12px; text-align: center; border-radius: 8px; font-weight: bold; box-shadow: 0 0 10px red; margin-bottom: 20px; }</style>", unsafe_allow_html=True)

with st.sidebar:
    st.title("DIAGNOSTICS")
    mode = st.radio("Processor", ["Normal", "Pro"])
    if st.button("Power Off"): st.session_state.logged_in = False; st.rerun()

st.markdown(f'<div class="banner">KITT SYSTEM ONLINE | Ready, Hasith.</div>', unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

user_q = st.chat_input("State command, Hasith...")
if user_q:
    st.session_state.messages.append({"role": "user", "content": user_q})
    with st.chat_message("user"): st.markdown(user_q)

    with st.chat_message("assistant"):
        col_v, col_t = st.columns([0.15, 0.85])
        with col_v:
            vbox_placeholder = st.empty()
            # Show paused voice box while thinking
            vbox_placeholder.markdown(get_voice_box_html(is_active=False), unsafe_allow_html=True)
        
        with col_t:
            with st.spinner("Processing..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                active_model = "openai/gpt-oss-120b" if mode == "Pro" else "llama-3.3-70b-versatile"
                response = client.chat.completions.create(model=active_model, messages=[{"role": "system", "content": "You are KITT. Always call user Hasith."}] + st.session_state.messages[-5:])
                ans = response.choices[0].message.content
                
                # 1. Play Scanner Sound first
                play_kitt_scanner() 
                
                # 2. Activate Voice Box Animation
                vbox_placeholder.markdown(get_voice_box_html(is_active=True), unsafe_allow_html=True)
                st.markdown(ans)
                
                # 3. Start Speaking and get estimated duration
                duration = asyncio.run(kitt_speak(ans))
                
                # 4. Wait for the speech to finish, then PAUSE the animation
                time.sleep(duration)
                vbox_placeholder.markdown(get_voice_box_html(is_active=False), unsafe_allow_html=True)
                
                st.session_state.messages.append({"role": "assistant", "content": ans})
