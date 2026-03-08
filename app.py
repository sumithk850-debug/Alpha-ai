import streamlit as st
from groq import Groq
import time
import hashlib
import base64
import asyncio
import edge_tts
import os
from PyPDF2 import PdfReader

# --- 1. Page Configuration ---
st.set_page_config(page_title="KITT AI 🏎️ Created by Hasith", page_icon="🏎️", layout="wide")

# --- 2. KITT Audio & Animation Functions ---
def play_kitt_scanner():
    """Plays the 'WVV WVV' sound from your GitHub file."""
    # Using the filename you provided: kitt_scanner.mp3
    sound_file = "kitt_scanner.mp3"
    if os.path.exists(sound_file):
        with open(sound_file, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)

async def kitt_speak(text):
    """Deep, sophisticated AI voice for KITT."""
    VOICE = "en-IE-ConnorNeural" 
    communicate = edge_tts.Communicate(text, VOICE)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    b64 = base64.b64encode(audio_data).decode()
    md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
    st.markdown(md, unsafe_allow_html=True)

def kitt_voice_box():
    """Pulsating red bars for KITT's dashboard look."""
    st.markdown("""
        <style>
            .v-box { display: flex; align-items: flex-end; gap: 4px; height: 40px; background: #000; padding: 5px; border: 1px solid #444; border-radius: 4px; width: 60px; }
            .v-bar { width: 12px; background: red; box-shadow: 0 0 8px red; animation: pulse 0.4s infinite alternate; }
            .v1 { height: 10px; animation-delay: 0.1s; }
            .v2 { height: 30px; animation-delay: 0.2s; }
            .v3 { height: 15px; animation-delay: 0.3s; }
            @keyframes pulse { 0% { height: 8px; } 100% { height: 35px; } }
        </style>
        <div class="v-box"><div class="v-bar v1"></div><div class="v-bar v2"></div><div class="v-bar v3"></div></div>
    """, unsafe_allow_html=True)

# --- 3. Loading Screen (Responsive & Fixed UI) ---
if "loaded" not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <style>
                .loader { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 85vh; background: #000; text-align: center; padding: 10px; }
                .k-text { font-size: 8vw; color: red; text-shadow: 0 0 15px red; font-family: monospace; margin-bottom: 20px; width: 100%; }
                .s-bar { width: 80%; max-width: 300px; height: 12px; background: #222; position: relative; border-radius: 6px; overflow: hidden; border: 1px solid #444; }
                .s-light { width: 60px; height: 100%; background: red; box-shadow: 0 0 20px red; position: absolute; animation: bounce 1.2s infinite alternate ease-in-out; }
                @keyframes bounce { 0% { left: 0%; } 100% { left: calc(100% - 60px); } }
            </style>
            <div class="loader">
                <div class="k-text">KITT INITIALIZING</div>
                <div class="s-bar"><div class="s-light"></div></div>
                <p style="color: #666; margin-top: 15px; font-size: 14px;">Knight Industries Two Thousand | Authorized: Hasith</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(7)
    st.session_state.loaded = True
    st.rerun()

# --- 4. Security System ---
if "user_db" not in st.session_state:
    st.session_state.user_db = {"matheesha": "123", "sadev": "123"}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center; color:red; font-family:monospace;">KITT SECURITY PORTAL</h1>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🔐 LOGIN", "📝 REGISTER", "⚡ CREATOR BYPASS"])
    
    with t1:
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("Access"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied.")
            
    with t2:
        reg_u = st.text_input("New ID")
        reg_p = st.text_input("New Pass", type="password")
        if st.button("Sign Up"):
            st.session_state.user_db[reg_u] = reg_p
            st.success("User registered!")

    with t3:
        bypass = st.text_input("Creator Master Key", key="bp")
        if st.button("Bypass Activation"):
            if bypass == "Hasith12378":
                st.session_state.logged_in, st.session_state.user = True, "Hasith"
                st.rerun()
            else: st.error("Master Key Invalid.")
    st.stop()

# --- 5. Main KITT Interface ---
st.markdown("<style>.stApp { background: #000; color: #fff; } .banner { background: linear-gradient(90deg, #900, #f00); padding: 12px; text-align: center; border-radius: 8px; font-weight: bold; box-shadow: 0 0 10px red; margin-bottom: 20px; }</style>", unsafe_allow_html=True)

with st.sidebar:
    st.title("DIAGNOSTICS")
    mode = st.radio("Processor Core", ["Normal (Llama 3.3)", "Pro (GPT OSS 120B)"])
    st.write("---")
    doc = st.file_uploader("Document Uplink", type=["pdf", "txt"])
    extracted_text = ""
    if doc:
        if doc.type == "application/pdf":
            reader = PdfReader(doc)
            extracted_text = "".join([p.extract_text() for p in reader.pages])
        else: extracted_text = doc.getvalue().decode()
    if st.button("Power Off"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown(f'<div class="banner">KITT SYSTEM ONLINE | Ready for Command, Hasith.</div>', unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

user_q = st.chat_input("State command, Hasith...")
if user_q:
    st.session_state.messages.append({"role": "user", "content": user_q})
    with st.chat_message("user"): st.markdown(user_q)

    with st.chat_message("assistant"):
        c1, c2 = st.columns([0.1, 0.9])
        with c1: kitt_voice_box() 
        with c2:
            with st.spinner("Processing..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                active_model = "openai/gpt-oss-120b" if "Pro" in mode else "llama-3.3-70b-versatile"
                sys_inst = f"You are KITT. Professional, dry-witted. Always address user as Hasith. Context: {extracted_text[:500]}"
                response = client.chat.completions.create(model=active_model, messages=[{"role": "system", "content": sys_inst}] + st.session_state.messages[-5:])
                ans = response.choices[0].message.content
                
                play_kitt_scanner() # Plays kitt_scanner.mp3
                st.markdown(ans)
                asyncio.run(kitt_speak(ans))
                st.session_state.messages.append({"role": "assistant", "content": ans})
