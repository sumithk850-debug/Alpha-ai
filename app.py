import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
import requests, base64, asyncio, io
import edge_tts
from PIL import Image
import time
import urllib.parse
import random  

# -----------------------
# 1. Page Config & Identity
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")

# --- GOOGLE VERIFICATION ---
st.markdown('<meta name="google-site-verification" content="W6jIGzCkkez2SpjygP6z0dJfinBNALmw2Hv-MkJvFB0" />', unsafe_allow_html=True)

# -----------------------
# 2. Session State Init
# -----------------------
if "messages" not in st.session_state: st.session_state.messages=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None

# -----------------------
# 3. Custom UI Styling (No Changes)
# -----------------------
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:20px; font-size: 22px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
    .stChatMessage { border-radius: 15px; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 45px; font-weight: bold; border: 1px solid #FFD700; transition: 0.3s; }
    div.stButton > button:hover { background-color: #FFD700; color: #000; }
    .lab-box { border: 1px solid #333; padding: 20px; border-radius: 15px; background: #0e1117; margin-bottom: 20px; border-left: 5px solid #FFD700; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# 4. Login System
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#FFD700; font-weight:bold;">Developed by Hasith</p>', unsafe_allow_html=True)
    name = st.text_input("Operator Name")
    password = st.text_input("Master Key", type="password")
    if st.button("Initialize Alpha"):
        if password == "Hasith12378":
            st.session_state.user_full_name = name or "Hasith"
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# -----------------------
# 5. API Setup (Using Secrets)
# -----------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

# -----------------------
# 6. FREE Music Function (Hugging Face)
# -----------------------
def generate_music_hf(prompt):
    try:
        API_URL = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=120)
        if response.status_code == 200: return response.content
        elif response.status_code == 503: return "loading"
        else: return None
    except: return None

# -----------------------
# 7. Sidebar Control
# -----------------------
with st.sidebar:
    st.title("Alpha Control")
    st.markdown(f"**Operator:** {st.session_state.user_full_name}")
    mode = st.radio("Level", ["Normal", "Pro"])
    voice_on = st.checkbox("Voice Output", value=True)
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# -----------------------
# 8. Multi-Modal Labs
# -----------------------
tab_img, tab_vid, tab_music = st.tabs(["🖼 Image Lab", "🎬 Video Lab", "🎵 Music Studio (Free)"])

# --- IMAGE LAB (Pollinations) ---
with tab_img:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    img_p = st.text_input("Describe image:")
    if st.button("Generate Photo"):
        if img_p:
            url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(img_p)}?nologo=true"
            st.image(url)
    st.markdown('</div>', unsafe_allow_html=True)

# --- VIDEO LAB (LTX-2) ---
with tab_vid:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    vid_p = st.text_input("Describe video scene:")
    if st.button("Generate Video"):
        if vid_p:
            with st.spinner("Rendering..."):
                v_url = f"https://gen.pollinations.ai/video/{urllib.parse.quote(vid_p)}?model=ltx-2&nologo=true"
                res = requests.get(v_url, headers={"Authorization": f"Bearer {POLLINATIONS_KEY}"})
                if res.status_code == 200: st.video(res.content)
    st.markdown('</div>', unsafe_allow_html=True)

# --- MUSIC STUDIO (Hugging Face - FREE) ---
with tab_music:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    music_p = st.text_input("Describe music (e.g. Chill lofi):")
    if st.button("Compose Music 🎶"):
        if music_p:
            with st.spinner("Alpha is composing... (Wait 1 min)"):
                for _ in range(3):
                    data = generate_music_hf(music_p)
                    if data == "loading":
                        time.sleep(20)
                        continue
                    elif data:
                        st.audio(data)
                        st.download_button("Download mp3", data, "alpha.mp3")
                        break
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# 9. Chat
# -----------------------
user_input = st.chat_input("Command Alpha...")
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"): st.markdown(user_input)
    with st.chat_message("assistant"):
        res = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are Alpha AI, created by Hasith."}] + st.session_state.messages
        )
        full_res = res.choices[0].message.content
        st.markdown(full_res)
        st.session_state.messages.append({"role":"assistant","content":full_res})

st.caption("Alpha AI | Created by Hasith")
