import streamlit as st
from groq import Groq
import time
import hashlib
import requests
import json
import base64
import asyncio
import edge_tts
import os
from PyPDF2 import PdfReader

# --- 1. Page Configuration (KITT Theme) ---
st.set_page_config(page_title="KITT 🏎️ Created by Hasith", page_icon="🏎️", layout="wide")

# --- 2. KITT Scanner Sound & Voice Functions ---
def play_kitt_scanner():
    """Plays the iconic KITT 'WVV WVV' scanner sound before speaking."""
    if os.path.exists("scanner.mp3"):
        with open("scanner.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)

async def kitt_speak(text):
    """Generates a deep, sophisticated male voice using Edge-TTS."""
    VOICE = "en-IE-ConnorNeural" # Deep, calm male voice suitable for KITT
    communicate = edge_tts.Communicate(text, VOICE)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    
    b64 = base64.b64encode(audio_data).decode()
    md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
    st.markdown(md, unsafe_allow_html=True)

# --- 3. KITT Loading Screen (7 Seconds) ---
if "loaded" not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <style>
                .loader-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; background-color: #000; }
                .kitt-text { font-size: 50px; font-weight: bold; color: #ff0000; text-shadow: 0 0 15px #ff0000; font-family: 'Courier New', monospace; }
                .scanner-bar { width: 300px; height: 10px; background: #333; position: relative; border-radius: 5px; overflow: hidden; border: 1px solid #444; }
                .scanner-light { width: 60px; height: 100%; background: red; box-shadow: 0 0 20px red; position: absolute; animation: scan 1.5s infinite ease-in-out; }
                @keyframes scan { 0% { left: -60px; } 50% { left: 240px; } 100% { left: -60px; } }
            </style>
            <div class="loader-container">
                <div class="kitt-text">🏎️ KITT INITIALIZING...</div>
                <div class="scanner-bar"><div class="scanner-light"></div></div>
                <p style="color: #666; margin-top: 15px;">Knight Industries Two Thousand | Authorized Access: Hasith</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(7)
    st.session_state.loaded = True
    placeholder.empty()
    st.rerun()

# --- 4. Custom UI Styling (KITT Red & Black) ---
st.markdown("""
<style>
    .stApp { background-color: #000; color: #fff; }
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #8B0000, #FF0000); color:#fff; border-radius:15px; text-align:center; font-weight:bold; box-shadow: 0 0 15px #FF0000; margin-bottom: 25px; }
    .stTextInput>div>div>input { background-color: #111; color: #FF0000; border: 1px solid #FF0000; }
    .stButton>button { background-color: #8B0000; color: white; border-radius: 10px; border: none; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 5. Security Portal with Creator Bypass ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center; color:red;">KITT 🏎️ ACCESS PORTAL</h1>', unsafe_allow_html=True)
    bypass_username = st.text_input("Enter Bypass ID (Hasith12378)", key="bypass_field").strip()
    
    if st.button("Activate KITT"):
        if bypass_username == "Hasith12378":
            st.session_state.logged_in = True
            st.session_state.current_user = "Hasith"
            st.rerun()
        else:
            st.error("Unauthorized Access! Access Denied.")
    st.stop()

# --- 6. Main Dashboard Logic ---
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/ff0000/car.png")
    st.subheader("System Diagnostics")
    ai_mode = st.radio("Intelligence Processor", ["Normal (Llama 3.3)", "Pro (GPT OSS 120B)"])
    
    st.write("---")
    st.subheader("Document Uplink")
    doc_file = st.file_uploader("Upload Data Files", type=["pdf", "txt"])
    extracted_text = ""
    if doc_file:
        if doc_file.type == "application/pdf":
            pdf_reader = PdfReader(doc_file)
            extracted_text = "".join([page.extract_text() for page in pdf_reader.pages])
        else:
            extracted_text = doc_file.getvalue().decode()

    if st.button("Shut Down System"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown(f'<div class="premium-banner">🏎️ KITT CORE OPERATIONAL | Hasith, I am ready for your commands.</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
user_query = st.chat_input("State your command, Hasith...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"): st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Processing data, Hasith..."):
            active_model = "openai/gpt-oss-120b" if "Pro" in ai_mode else "llama-3.3-70b-versatile"
            sys_inst = f"You are KITT, the advanced AI car from Knight Rider. You are loyal, professional, and dry-witted. Always call the user 'Hasith'. Context: {extracted_text[:1000]}"
            
            chat_payload = [{"role": "system", "content": sys_inst}] + st.session_state.messages[-5:]

            try:
                response = client_groq.chat.completions.create(model=active_model, messages=chat_payload)
                ans = response.choices[0].message.content
                
                # Execution Sequence: Scanner Sound -> Show Text -> Deep Voice
                play_kitt_scanner()
                time.sleep(0.5)
                st.markdown(ans)
                asyncio.run(kitt_speak(ans))
                
                st.session_state.messages.append({"role": "assistant", "content": ans})
            except Exception as e:
                st.error(f"System Malfunction: {e}")
