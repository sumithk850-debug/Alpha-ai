import streamlit as st
from groq import Groq
import time
import base64
import asyncio
import edge_tts
import os
import speech_recognition as sr
import webbrowser
from PyPDF2 import PdfReader

# --- 1. Page Configuration & Cyber UI ---
st.set_page_config(page_title="Alpha AI | Next-Gen", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #02050a; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    .alpha-neon-title {
        font-size: clamp(2.5em, 8vw, 4em);
        font-weight: 900;
        text-align: center;
        color: #fff;
        text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff, 0 0 40px #00d4ff;
        letter-spacing: clamp(5px, 3vw, 12px);
        margin-bottom: 10px;
        font-family: 'Orbitron', sans-serif;
    }
    
    .glass-card {
        background: rgba(0, 212, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 212, 255, 0.2);
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    }

    .hasith-badge {
        background: linear-gradient(135deg, #001f3f, #0074d9);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #00d4ff;
        text-align: center;
    }

    /* Neural Pulse Loader */
    .loader-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 80vh;
        width: 100%;
    }
    .alpha-load-text {
        color: #00d4ff; 
        margin-top: 30px; 
        letter-spacing: clamp(8px, 4vw, 15px); 
        padding-left: 15px;
        font-weight: bold;
        text-align: center;
        font-size: clamp(1.5em, 6vw, 2.5em);
    }
    .pulse-ring {
        width: 80px; height: 80px;
        border: 4px solid #00d4ff;
        border-radius: 50%;
        animation: ring-pulse 1.5s infinite ease-out;
    }
    @keyframes ring-pulse {
        0% { transform: scale(0.6); opacity: 1; }
        100% { transform: scale(1.4); opacity: 0; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. Mobile & Web OS Controller Logic ---
def execute_mobile_command(text):
    cmd = text.lower()
    if "open youtube" in cmd:
        webbrowser.open("https://www.youtube.com")
        return "Initiating YouTube interface, Hasith."
    elif "open maps" in cmd:
        webbrowser.open("https://maps.google.com")
        return "Accessing satellite navigation core, Hasith."
    elif "open whatsapp" in cmd:
        webbrowser.open("https://web.whatsapp.com")
        return "Connecting to communication relay."
    elif "open mail" in cmd or "open gmail" in cmd:
        webbrowser.open("https://mail.google.com")
        return "Opening secure mailing terminal."
    elif "search" in cmd:
        query = cmd.replace("search", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Retrieving data for: {query}."
    return None

# --- 3. Speech Recognition Engine ---
def listen_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.8)
        try:
            audio = recognizer.listen(source, timeout=5)
            # Try English (US) as primary for commands
            text = recognizer.recognize_google(audio, language="en-US")
            return text
        except:
            return ""

# --- 4. Alpha Audio & Logic Functions ---
async def speak_alpha(text):
    VOICE = "en-US-SteffanNeural"
    communicate = edge_tts.Communicate(text, VOICE)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    b64 = base64.b64encode(audio_data).decode()
    st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    return len(audio_data) / 15500

def type_effect(text, container):
    full = ""
    for char in text:
        full += char
        container.markdown(f"<div style='font-size:1.1em; line-height:1.6;'>{full} ⚡</div>", unsafe_allow_html=True)
        time.sleep(0.01)
    container.markdown(full)

# --- 5. Initializing Sequence ---
if "loaded" not in st.session_state:
    l_box = st.empty()
    with l_box.container():
        st.markdown("""
            <div class="loader-container">
                <div class="pulse-ring"></div>
                <div class="alpha-load-text">ALPHA AI</div>
                <p style="color:#00d4ff; font-size:10px; margin-top:10px; letter-spacing:3px;">CALIBRATING QUANTUM CORE | CREATOR: HASITH</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(4)
    st.session_state.loaded = True
    st.rerun()

# --- 6. Security System ---
if "user_db" not in st.session_state: st.session_state.user_db = {"matheesha": "123", "sadev": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="alpha-neon-title">ALPHA CORE</div>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🔐 LOGIN", "📝 REGISTER", "⚡ CREATOR"])
    with t1:
        u = st.text_input("Operator ID").lower()
        p = st.text_input("Access Key", type="password")
        if st.button("Unlock Core"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
    with t2:
        reg_u = st.text_input("New Identity")
        reg_p = st.text_input("New Security Key", type="password")
        if st.button("Register Identity"): st.session_state.user_db[reg_u] = reg_p
    with t3:
        bypass = st.text_input("Master Key", key="bp")
        if st.button("Bypass Security"):
            if bypass == "Hasith12378":
                st.session_state.logged_in, st.session_state.user = True, "Hasith"
                st.rerun()
    st.stop()

# --- 7. Alpha Dashboard ---
with st.sidebar:
    st.markdown(f"""
        <div class="hasith-badge">
            <small style="color:rgba(255,255,255,0.6);">SYSTEM ARCHITECT</small><br>
            <b style="font-size:1.3em; color:#00d4ff;">HASITH</b>
        </div>
    """, unsafe_allow_html=True)
    st.write("---")
    
    if st.button("🎙️ VOICE COMMAND"):
        with st.spinner("Listening..."):
            v_input = listen_voice()
            if v_input:
                st.session_state.voice_data = v_input
                st.rerun()

    mode = st.radio("Processor Unit", ["Llama 3.3 (Normal)", "GPT OSS 120B (Pro)"])
    st.write("---")
    doc = st.file_uploader("Data Linkage", type=["pdf", "txt"])
    extracted = ""
    if doc:
        if doc.type == "application/pdf":
            reader = PdfReader(doc); extracted = "".join([p.extract_text() for p in reader.pages])
        else: extracted = doc.getvalue().decode()
        
    if st.button("🔌 Disconnect"): st.session_state.logged_in = False; st.rerun()

st.markdown('<div class="alpha-neon-title">ALPHA AI</div>', unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []

# Status Summary (Hides after first message)
summary_ph = st.empty()
if len(st.session_state.messages) == 0:
    summary_ph.markdown("""<div class="glass-card">
        <h3 style="color:#00d4ff; margin:0;">💠 SYSTEM CAPABILITIES</h3>
        <p style='color:#888;'>Voice Commands, OS Control, and Neural Reasoning Active.<br>Ready, Hasith.</p>
    </div>""", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

user_input = st.chat_input("State command, Hasith...")
if "voice_data" in st.session_state:
    user_input = st.session_state.voice_data
    del st.session_state.voice_data

if user_input:
    summary_ph.empty()
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        text_target = st.empty()
        
        # OS Control Logic
        mobile_msg = execute_mobile_command(user_input)
        
        if mobile_msg:
            ans = mobile_msg
        else:
            with st.spinner("Alpha is thinking..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                model_engine = "openai/gpt-oss-120b" if "Pro" in mode else "llama-3.3-70b-versatile"
                response = client.chat.completions.create(
                    model=model_engine,
                    messages=[{"role":"system","content":f"You are Alpha AI. Professional. Developed by Hasith. Address user as Hasith. Data: {extracted[:200]}"}] + st.session_state.messages[-5:]
                )
                ans = response.choices[0].message.content
            
        dur = asyncio.run(speak_alpha(ans))
        type_effect(ans, text_target)
        st.session_state.messages.append({"role": "assistant", "content": ans})
