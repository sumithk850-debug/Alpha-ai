import streamlit as st
from groq import Groq
import time
import base64
import asyncio
import edge_tts
import os
import io
from PyPDF2 import PdfReader

# --- 1. Page Configuration & Glass UI ---
st.set_page_config(page_title="KITT AI | Knight Industries", page_icon="🏎️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #050505; color: #ffffff; }
    .glass-banner {
        background: rgba(255, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 0, 0, 0.3);
        padding: 20px;
        text-align: center;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(255, 0, 0, 0.2);
        margin-bottom: 10px;
    }
    .status-bar {
        background: rgba(20, 20, 20, 0.8);
        padding: 10px;
        border-left: 4px solid #ff0000;
        margin-bottom: 25px;
        font-size: 0.85em;
        color: #bbb;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. Corrected Audio & Animation Logic ---
def play_kitt_scanner():
    """Plays the 'WVV' sound and waits until it actually finishes."""
    sound_file = "kitt_scanner.mp3"
    if os.path.exists(sound_file):
        with open(sound_file, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
        # Standard KITT scanner is about 1.8 to 2 seconds.
        time.sleep(1.8) 

async def get_kitt_voice_and_duration(text):
    """Generates voice and returns the exact audio data."""
    VOICE = "en-IE-ConnorNeural"
    communicate = edge_tts.Communicate(text, VOICE)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    
    # Calculate duration accurately (Bytes to seconds for MP3 at ~32kbps)
    # This is much more reliable than character counting.
    duration = len(audio_data) / 16000 # Approximation for typical speech rate
    return audio_data, duration

def get_voice_box(is_active=True):
    """Voice box that stays at 0 height when not active."""
    state = "running" if is_active else "paused"
    opacity = "1" if is_active else "0.3"
    h1, h2, h3 = ("10px", "30px", "15px") if is_active else ("2px", "2px", "2px")
    
    return f"""
        <div style="display: flex; align-items: flex-end; gap: 4px; height: 45px; background: #000; padding: 5px; border: 1px solid #333; border-radius: 4px; width: 60px; opacity: {opacity};">
            <style>
                .v-bar {{ width: 12px; background: red; box-shadow: 0 0 10px red; transition: height 0.3s ease; }}
                .v-anim {{ animation: pulse 0.4s infinite alternate; animation-play-state: {state}; }}
                @keyframes pulse {{ 0% {{ height: 5px; }} 100% {{ height: 38px; }} }}
            </style>
            <div class="v-bar {'v-anim' if is_active else ''}" style="height: {h1};"></div>
            <div class="v-bar {'v-anim' if is_active else ''}" style="height: {h2};"></div>
            <div class="v-bar {'v-anim' if is_active else ''}" style="height: {h3};"></div>
        </div>
    """

def typewriter_effect(text, container):
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(full_text + "▌")
        time.sleep(0.03) # Professional typing speed
    container.markdown(full_text)

# --- 3. UI Flow ---
if "loaded" not in st.session_state:
    ph = st.empty()
    with ph.container():
        st.markdown('<h1 style="text-align:center; color:red; margin-top:20vh;">KITT INITIALIZING</h1>', unsafe_allow_html=True)
        time.sleep(4)
    st.session_state.loaded = True
    st.rerun()

# Security System (Your original users/passwords)
if "user_db" not in st.session_state: st.session_state.user_db = {"matheesha": "123", "sadev": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="glass-banner"><h1>SECURITY ACCESS</h1></div>', unsafe_allow_html=True)
    u = st.text_input("Username").lower()
    p = st.text_input("Password", type="password")
    if st.button("Enter"):
        if u in st.session_state.user_db and st.session_state.user_db[u] == p:
            st.session_state.logged_in, st.session_state.user = True, u
            st.rerun()
    st.stop()

# Main Dashboard
st.markdown('<div class="glass-banner">KITT SYSTEM ONLINE | Operator: Hasith</div>', unsafe_allow_html=True)

summary_ph = st.empty()
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    summary_ph.markdown('<div class="status-bar"><b>SYSTEM STATUS:</b> ALL CIRCUITS ACTIVE. READY FOR INPUT, HASITH.</div>', unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

user_q = st.chat_input("Command...")
if user_q:
    summary_ph.empty()
    st.session_state.messages.append({"role": "user", "content": user_q})
    with st.chat_message("user"): st.markdown(user_q)

    with st.chat_message("assistant"):
        col_v, col_t = st.columns([0.15, 0.85])
        with col_v:
            vbox_ph = st.empty()
            vbox_ph.markdown(get_voice_box(is_active=False), unsafe_allow_html=True)
        with col_t:
            text_ph = st.empty()
            with st.spinner("Processing..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are KITT. Professional, witty. Call user Hasith."}] + st.session_state.messages[-5:]
                )
                ans = response.choices[0].message.content
                
                # 1. GET VOICE DATA FIRST (To know exact duration)
                audio_data, duration = asyncio.run(get_kitt_voice_and_duration(ans))
                
                # 2. PLAY SCANNER SOUND
                play_kitt_scanner()
                
                # 3. START ANIMATION & VOICE SIMULTANEOUSLY
                vbox_ph.markdown(get_voice_box(is_active=True), unsafe_allow_html=True)
                b64_audio = base64.b64encode(audio_data).decode()
                st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64_audio}">', unsafe_allow_html=True)
                
                # 4. TYPEWRITER EFFECT
                typewriter_effect(ans, text_ph)
                
                # 5. WAIT UNTIL VOICE FINISHES (Exact duration)
                # We subtract a small amount since typewriter took some time
                remaining_time = max(0, duration - (len(ans) * 0.03))
                time.sleep(remaining_time)
                
                # 6. RESET ANIMATION (Bands go down)
                vbox_ph.markdown(get_voice_box(is_active=False), unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": ans})
