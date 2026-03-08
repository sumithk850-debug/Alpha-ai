import streamlit as st
from groq import Groq
import time
import base64
import asyncio
import edge_tts
import os
from PyPDF2 import PdfReader

# --- 1. Page Configuration & Glass UI CSS ---
st.set_page_config(page_title="KITT AI | Knight Industries", page_icon="🏎️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #050505; color: #ffffff; font-family: 'Segoe UI', Roboto, Helvetica; }
    
    /* Glassmorphism Effect for Banner */
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
    
    /* Professional Status Bar */
    .status-bar {
        background: rgba(20, 20, 20, 0.8);
        padding: 10px;
        border-left: 4px solid #ff0000;
        margin-bottom: 25px;
        font-size: 0.85em;
        color: #bbb;
        letter-spacing: 1px;
    }

    /* KITT Scanner Animation (Responsive) */
    .s-bar { width: 80%; max-width: 300px; height: 10px; background: #111; position: relative; border-radius: 5px; overflow: hidden; border: 1px solid #333; margin: 20px auto; }
    .s-light { width: 60px; height: 100%; background: red; box-shadow: 0 0 20px red; position: absolute; animation: bounce 1.2s infinite alternate ease-in-out; }
    @keyframes bounce { 0% { left: 0%; } 100% { left: calc(100% - 60px); } }
    </style>
""", unsafe_allow_html=True)

# --- 2. Advanced KITT Functions ---
def play_kitt_scanner():
    """Plays the signature 'WVV' sound and pauses for effect."""
    sound_file = "kitt_scanner.mp3"
    if os.path.exists(sound_file):
        with open(sound_file, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
        time.sleep(1.8) # Allow scanner sound to finish before voice starts

async def kitt_speak(text):
    """Generates KITT's voice and handles timing."""
    VOICE = "en-IE-ConnorNeural" 
    communicate = edge_tts.Communicate(text, VOICE)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    b64 = base64.b64encode(audio_data).decode()
    st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    return max(len(text) / 14, 2)

def get_voice_box(is_active=True):
    """Dynamic Voice Box with zero-height bars when idle."""
    state = "running" if is_active else "paused"
    opacity = "1" if is_active else "0.3"
    return f"""
        <div style="display: flex; align-items: flex-end; gap: 4px; height: 45px; background: #000; padding: 5px; border: 1px solid #333; border-radius: 4px; width: 60px; opacity: {opacity};">
            <style>
                .v-bar {{ width: 12px; background: red; box-shadow: 0 0 10px red; }}
                .v-anim {{ animation: pulse 0.4s infinite alternate; animation-play-state: {state}; }}
                @keyframes pulse {{ 0% {{ height: 8px; }} 100% {{ height: 38px; }} }}
            </style>
            <div class="v-bar {'v-anim' if is_active else ''}" style="height: {'10px' if is_active else '4px'};"></div>
            <div class="v-bar {'v-anim' if is_active else ''}" style="height: {'30px' if is_active else '4px'};"></div>
            <div class="v-bar {'v-anim' if is_active else ''}" style="height: {'15px' if is_active else '4px'};"></div>
        </div>
    """

def typewriter_effect(text, container):
    """Renders text one character at a time for a professional computer look."""
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(full_text + "▌")
        time.sleep(0.02)
    container.markdown(full_text)

# --- 3. Loading Screen ---
if "loaded" not in st.session_state:
    ph = st.empty()
    with ph.container():
        st.markdown('<div style="height: 30vh;"></div>', unsafe_allow_html=True)
        st.markdown('<h1 style="text-align:center; color:red; font-size:6vw;">KITT INITIALIZING</h1>', unsafe_allow_html=True)
        st.markdown('<div class="s-bar"><div class="s-light"></div></div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#555;">KNIGHT INDUSTRIES TWO THOUSAND | ACCESS GRANTED: HASITH</p>', unsafe_allow_html=True)
        time.sleep(6)
    st.session_state.loaded = True
    st.rerun()

# --- 4. Enhanced Security Portal ---
if "user_db" not in st.session_state: st.session_state.user_db = {"matheesha": "123", "sadev": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="glass-banner"><h1>SECURITY AUTHENTICATION REQUIRED</h1></div>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🔐 LOGIN", "📝 REGISTER", "⚡ CREATOR BYPASS"])
    with t1:
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("Access Interface"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
    with t2:
        reg_u = st.text_input("Assign New ID")
        reg_p = st.text_input("Assign Secret Key", type="password")
        if st.button("Initialize Registration"):
            st.session_state.user_db[reg_u] = reg_p
            st.success("New user uplink established.")
    with t3:
        bypass = st.text_input("Creator Master Key (Hasith Only)", key="bp")
        if st.button("Bypass Security Protocol"):
            if bypass == "Hasith12378":
                st.session_state.logged_in, st.session_state.user = True, "Hasith"
                st.rerun()
    st.stop()

# --- 5. Main KITT Dashboard ---
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/ff0000/car.png")
    st.title("DIAGNOSTICS")
    mode = st.radio("Processor Core", ["Llama 3.3 (High Speed)", "GPT OSS (Deep Analysis)"])
    st.write("---")
    doc = st.file_uploader("Data Uplink (PDF/TXT)", type=["pdf", "txt"])
    extracted_text = ""
    if doc:
        if doc.type == "application/pdf":
            reader = PdfReader(doc); extracted_text = "".join([p.extract_text() for p in reader.pages])
        else: extracted_text = doc.getvalue().decode()
    if st.button("Deactivate KITT"):
        st.session_state.logged_in = False; st.rerun()

st.markdown('<div class="glass-banner">KITT SYSTEM ONLINE | Authorized Operator: Hasith</div>', unsafe_allow_html=True)

# SUMMARY (Hides after first command)
summary_ph = st.empty()
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    summary_ph.markdown("""<div class="status-bar">
        <b>SYSTEM STATUS:</b> ONLINE | <b>MODULATOR:</b> ACTIVE | <b>CPU:</b> STABLE <br>
        <b>WELCOME, HASITH.</b> I am ready to assist you with any task.
    </div>""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

user_q = st.chat_input("Input Command, Hasith...")
if user_q:
    summary_ph.empty()
    st.session_state.messages.append({"role": "user", "content": user_q})
    with st.chat_message("user"): st.markdown(user_q)

    with st.chat_message("assistant"):
        col_v, col_t = st.columns([0.1, 0.9])
        with col_v:
            vbox_ph = st.empty()
            vbox_ph.markdown(get_voice_box(is_active=False), unsafe_allow_html=True)
        
        with col_t:
            text_ph = st.empty()
            with st.spinner("Analyzing..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                model_name = "openai/gpt-oss-120b" if "GPT" in mode else "llama-3.3-70b-versatile"
                response = client.chat.completions.create(
                    model=model_name, 
                    messages=[{"role": "system", "content": f"You are KITT. Professional, analytical, dry-witted. Address user as Hasith. Data: {extracted_text[:400]}"}] + st.session_state.messages[-5:]
                )
                ans = response.choices[0].message.content
                
                # EXECUTION SEQUENCE
                play_kitt_scanner() # 1. Scanner Sound (Pre-speech)
                vbox_ph.markdown(get_voice_box(is_active=True), unsafe_allow_html=True) # 2. Start Animation
                
                duration = asyncio.run(kitt_speak(ans)) # 3. Start Voice
                typewriter_effect(ans, text_ph) # 4. Typewriter Effect (Synced with voice start)
                
                time.sleep(2) # Final buffer
                vbox_ph.markdown(get_voice_box(is_active=False), unsafe_allow_html=True) # 5. Reset Animation
                st.session_state.messages.append({"role": "assistant", "content": ans})
