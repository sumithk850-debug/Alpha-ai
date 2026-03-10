import streamlit as st
from groq import Groq
import time
import base64
import asyncio
import edge_tts
import os
from PyPDF2 import PdfReader

# --- 1. Page Configuration & Cyber UI ---
st.set_page_config(page_title="Alpha AI | Next-Gen", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #02050a; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    /* Neon Glow Title for Alpha AI */
    .alpha-neon-title {
        font-size: clamp(2.5em, 8vw, 4em); /* Responsive font size */
        font-weight: 900;
        text-align: center;
        color: #fff;
        text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff, 0 0 40px #00d4ff;
        letter-spacing: clamp(5px, 3vw, 12px);
        margin-bottom: 5px;
        font-family: 'Orbitron', sans-serif;
    }
    
    .glass-card {
        background: rgba(0, 212, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 212, 255, 0.2);
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }

    .status-capsule {
        background: rgba(0, 0, 0, 0.6);
        border-left: 5px solid #00d4ff;
        padding: 12px;
        border-radius: 10px;
        font-size: 0.9em;
        color: #00d4ff;
    }

    .hasith-badge {
        background: linear-gradient(135deg, #001f3f, #0074d9);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #00d4ff;
        text-align: center;
    }

    /* 📱 Enhanced Loading Screen for Mobile */
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
        font-weight: bold;
        padding-left: 15px; /* Shifts text slightly to the right */
        text-align: center;
        font-size: clamp(1.5em, 6vw, 2.5em);
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }

    .pulse-ring {
        width: 80px; height: 80px;
        border: 4px solid #00d4ff;
        border-radius: 50%;
        animation: ring-pulse 1.5s infinite ease-out;
        box-shadow: 0 0 20px #00d4ff;
    }
    @keyframes ring-pulse {
        0% { transform: scale(0.6); opacity: 1; }
        100% { transform: scale(1.4); opacity: 0; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. Advanced Audio & Logic Functions ---
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
        time.sleep(0.02)
    container.markdown(full)

# --- 3. Alpha Loading Screen ---
if "loaded" not in st.session_state:
    l_box = st.empty()
    with l_box.container():
        st.markdown("""
            <div class="loader-container">
                <div class="pulse-ring"></div>
                <div class="alpha-load-text">ALPHA AI</div>
                <p style="color:#444; font-size:10px; margin-top:10px; letter-spacing:2px;">INITIALIZING QUANTUM CORE</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(5)
    st.session_state.loaded = True
    st.rerun()

# --- 4. Restored Security System ---
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

# --- 5. Alpha Dashboard ---
with st.sidebar:
    st.markdown(f"""
        <div class="hasith-badge">
            <small style="color:rgba(255,255,255,0.6);">SYSTEM ARCHITECT</small><br>
            <b style="font-size:1.3em; color:#00d4ff;">HASITH</b>
        </div>
    """, unsafe_allow_html=True)
    st.write("---")
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

summary_placeholder = st.empty()
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    summary_placeholder.markdown(f"""
        <div class="glass-card">
            <h3 style="color:#00d4ff; margin:0;">💠 SYSTEM CAPABILITIES</h3>
            <div class="status-capsule">
                • <b>LLM CORES:</b> Llama 3.3 & GPT OSS-120B Integration.<br>
                • <b>DEVELOPER:</b> Designed and Optimized by <b>Hasith</b>.<br>
                • <b>STATUS:</b> All quantum circuits operational.
            </div>
        </div>
    """, unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

user_input = st.chat_input("State command, Hasith...")
if user_input:
    summary_placeholder.empty()
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        text_target = st.empty()
        with st.spinner("Alpha is thinking..."):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            model_engine = "openai/gpt-oss-120b" if "Pro" in mode else "llama-3.3-70b-versatile"
            response = client.chat.completions.create(
                model=model_engine,
                messages=[{"role":"system","content":"You are Alpha AI. Professional and advanced. Address user as Hasith."}] + st.session_state.messages[-5:]
            )
            ans = response.choices[0].message.content
            
            dur = asyncio.run(speak_alpha(ans))
            type_effect(ans, text_target)
            
            time.sleep(max(0, dur - (len(ans) * 0.02)))
            st.session_state.messages.append({"role": "assistant", "content": ans})
