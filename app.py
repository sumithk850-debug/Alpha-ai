import streamlit as st
from groq import Groq
import time
import base64
import asyncio
import edge_tts
import os
from PyPDF2 import PdfReader

# --- 1. Page Configuration & Professional UI ---
st.set_page_config(page_title="KITT AI | Knight Industries", page_icon="🏎️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #000000; color: #ffffff; font-family: 'Courier New', Courier, monospace; }
    
    /* 🏎️ KITT Loading Screen Styles */
    .loader-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 85vh;
        background: #000;
        text-align: center;
    }
    .k-text {
        font-size: 7vw;
        color: red;
        text-shadow: 0 0 20px red;
        font-weight: bold;
        letter-spacing: 5px;
        margin-bottom: 30px;
    }
    .scanner-track {
        width: 350px;
        height: 15px;
        background: #111;
        border: 2px solid #333;
        border-radius: 8px;
        position: relative;
        overflow: hidden;
    }
    .scanner-light {
        width: 80px;
        height: 100%;
        background: linear-gradient(90deg, transparent, red, transparent);
        box-shadow: 0 0 15px red;
        position: absolute;
        animation: scan 1.5s infinite alternate ease-in-out;
    }
    @keyframes scan {
        0% { left: -10%; }
        100% { left: 85%; }
    }
    .boot-info {
        color: #555;
        font-size: 14px;
        margin-top: 20px;
        text-transform: uppercase;
    }

    /* Professional Dashboard Elements */
    .glass-banner {
        background: rgba(255, 0, 0, 0.05);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 0, 0, 0.3);
        padding: 20px;
        text-align: center;
        border-radius: 12px;
        box-shadow: 0 4px 30px rgba(255, 0, 0, 0.1);
        margin-bottom: 10px;
    }
    .status-bar {
        background: #0a0a0a;
        padding: 12px;
        border-left: 4px solid #ff0000;
        margin-bottom: 20px;
        font-size: 0.85em;
        color: #888;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. KITT Functions ---
def play_kitt_scanner():
    """WVV WVV sound plays and pauses for 1.8s."""
    sound_file = "kitt_scanner.mp3"
    if os.path.exists(sound_file):
        with open(sound_file, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
        time.sleep(1.8) 

async def get_voice_data(text):
    """Generates voice and calculates exact timing."""
    VOICE = "en-IE-ConnorNeural"
    communicate = edge_tts.Communicate(text, VOICE)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    # Sync: roughly 15.5k bytes per second
    duration = len(audio_data) / 15500 
    return audio_data, duration

def get_voice_box(is_active=True):
    state = "running" if is_active else "paused"
    opacity = "1" if is_active else "0.3"
    h_val = "10px" if is_active else "4px"
    return f"""
        <div style="display: flex; align-items: flex-end; gap: 4px; height: 45px; background: #000; padding: 5px; border: 1px solid #333; border-radius: 4px; width: 65px; opacity: {opacity};">
            <style>
                .v-bar {{ width: 12px; background: red; box-shadow: 0 0 10px red; }}
                .v-anim {{ animation: pulse 0.4s infinite alternate; animation-play-state: {state}; }}
                @keyframes pulse {{ 0% {{ height: 8px; }} 100% {{ height: 40px; }} }}
            </style>
            <div class="v-bar {'v-anim' if is_active else ''}" style="height: {h_val};"></div>
            <div class="v-bar {'v-anim' if is_active else ''}" style="height: {h_val};"></div>
            <div class="v-bar {'v-anim' if is_active else ''}" style="height: {h_val};"></div>
        </div>
    """

def typewriter(text, placeholder):
    full = ""
    for char in text:
        full += char
        placeholder.markdown(full + "▌")
        time.sleep(0.025)
    placeholder.markdown(full)

# --- 3. THE LOADING SCREEN ---

if "loaded" not in st.session_state:
    l_screen = st.empty()
    with l_screen.container():
        st.markdown(f"""
            <div class="loader-container">
                <div class="k-text">KITT INITIALIZING</div>
                <div class="scanner-track"><div class="scanner-light"></div></div>
                <div class="boot-info">
                    MEMORY CHECK: OK | SYSTEM CPU: STABLE | SAT COM: LINKED <br>
                    <span style="color:red;">AUTHORIZED OPERATOR: HASITH</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(6) # Professional loading duration
    st.session_state.loaded = True
    st.rerun()

# --- 4. Security System ---
if "user_db" not in st.session_state:
    st.session_state.user_db = {"matheesha": "123", "sadev": "123"}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="glass-banner"><h1>KITT SECURITY PORTAL</h1></div>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🔐 LOGIN", "📝 REGISTER", "⚡ CREATOR"])
    with t1:
        u = st.text_input("ID").lower()
        p = st.text_input("KEY", type="password")
        if st.button("AUTHENTICATE"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
    with t2:
        nu = st.text_input("New ID")
        np = st.text_input("New KEY", type="password")
        if st.button("CREATE"): st.session_state.user_db[nu] = np
    with t3:
        bypass = st.text_input("MASTER KEY", key="bp")
        if st.button("OVERRIDE"):
            if bypass == "Hasith12378":
                st.session_state.logged_in, st.session_state.user = True, "Hasith"
                st.rerun()
    st.stop()

# --- 5. Main Dashboard ---
with st.sidebar:
    st.title("DIAGNOSTICS")
    mode = st.radio("Core", ["Normal Mode", "Pro Mode (GPT OSS)"])
    doc = st.file_uploader("Data Uplink", type=["pdf", "txt"])
    extracted = ""
    if doc:
        if doc.type == "application/pdf":
            reader = PdfReader(doc); extracted = "".join([p.extract_text() for p in reader.pages])
        else: extracted = doc.getvalue().decode()
    if st.button("SHUTDOWN"): st.session_state.logged_in = False; st.rerun()

st.markdown('<div class="glass-banner">KITT SYSTEM ONLINE | Authorized: Hasith</div>', unsafe_allow_html=True)

# Status Summary
summary_ph = st.empty()
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    summary_ph.markdown("""<div class="status-bar">
        <b>SYSTEM STATUS:</b> ALL CIRCUITS ACTIVE | <b>SCANNER:</b> SYNCED | <b>LOCATION:</b> Sri Lanka <br>
        Ready for command, Hasith.
    </div>""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("State command, Hasith...")
if u_input:
    summary_ph.empty()
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    with st.chat_message("assistant"):
        cv, ct = st.columns([0.15, 0.85])
        with cv: 
            vbox = st.empty()
            vbox.markdown(get_voice_box(is_active=False), unsafe_allow_html=True)
        with ct:
            text_box = st.empty()
            with st.spinner("Analyzing..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                m_type = "openai/gpt-oss-120b" if "Pro" in mode else "llama-3.3-70b-versatile"
                resp = client.chat.completions.create(model=m_type, messages=[{"role":"system","content":"You are KITT AI. Call user Hasith."}] + st.session_state.messages[-5:])
                ans = resp.choices[0].message.content
                
                audio, dur = asyncio.run(get_voice_data(ans))
                
                play_kitt_scanner() # Plays BEFORE voice
                vbox.markdown(get_voice_box(is_active=True), unsafe_allow_html=True)
                
                b64 = base64.b64encode(audio).decode()
                st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
                
                typewriter(ans, text_box)
                
                # Wait for voice to finish
                time.sleep(max(0, dur - (len(ans)*0.025)))
                vbox.markdown(get_voice_box(is_active=False), unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": ans})
