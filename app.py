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
# 1. Page Config & Identity (Created by Hasith)
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")

# -----------------------
# 2. Session State Init
# -----------------------
if "messages" not in st.session_state: st.session_state.messages=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None

# -----------------------
# 3. Custom UI Styling
# -----------------------
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:20px; font-size: 22px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
    .lab-box { border: 1px solid #333; padding: 20px; border-radius: 15px; background: #0e1117; margin-bottom: 20px; border-left: 5px solid #FFD700; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 45px; font-weight: bold; border: 1px solid #FFD700; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# 4. Login System
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    name = st.text_input("Operator Name")
    password = st.text_input("Master Key", type="password")
    if st.button("Initialize Alpha"):
        if password == "Hasith12378":
            st.session_state.user_full_name = name or "Hasith"
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# -----------------------
# 5. API Setup
# -----------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

# -----------------------
# 6. Audio/Music Generation Function
# -----------------------
def generate_music_pollinations(prompt):
    try:
        encoded_p = urllib.parse.quote(prompt)
        # Documentation එකේ තිබූ GET /audio/{text} endpoint එක
        url = f"https://gen.pollinations.ai/audio/{encoded_p}"
        
        headers = {
            "Authorization": f"Bearer {POLLINATIONS_KEY}"
        }
        
        response = requests.get(url, headers=headers, timeout=120)
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Audio Error: {response.status_code}")
            return None
    except Exception as e:
        return None

# -----------------------
# 7. Sidebar
# -----------------------
with st.sidebar:
    st.title("Alpha Control")
    st.write(f"Operator: {st.session_state.user_full_name}")
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown(f'<div class="premium-banner">⚡ ALPHA AI | MULTIMODAL LABS</div>', unsafe_allow_html=True)

# -----------------------
# 8. Labs (Image, Video, AND MUSIC)
# -----------------------
tab_img, tab_vid, tab_music = st.tabs(["🖼 Image Lab", "🎬 Video Lab", "🎵 Music Lab"])

# --- IMAGE LAB ---
with tab_img:
    img_p = st.text_input("Image Description:")
    if st.button("Generate Image"):
        if img_p:
            img_url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(img_p)}?nologo=true"
            st.image(img_url)

# --- VIDEO LAB (Using LTX-2) ---
with tab_vid:
    vid_p = st.text_input("Video Scene Description:")
    if st.button("Generate Video"):
        if vid_p:
            with st.spinner("Alpha is rendering video..."):
                v_url = f"https://gen.pollinations.ai/video/{urllib.parse.quote(vid_p)}?model=ltx-2&nologo=true"
                headers = {"Authorization": f"Bearer {POLLINATIONS_KEY}"}
                res = requests.get(v_url, headers=headers)
                if res.status_code == 200:
                    st.video(res.content)

# --- 🔥 NEW: MUSIC LAB ---
with tab_music:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    music_p = st.text_input("Describe the music (e.g., 'Lo-fi hip hop beat' or 'Cinematic epic drums'):")
    if st.button("Compose Music 🎶"):
        if music_p:
            with st.spinner("Alpha is composing your track..."):
                music_data = generate_music_pollinations(music_p)
                if music_data:
                    st.audio(music_data, format="audio/mp3")
                    st.download_button("Download Music 📥", music_data, "alpha_music.mp3")
                else:
                    st.warning("Could not generate music. Check your Pollen balance.")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# 9. Chat System
# -----------------------
st.divider()
user_input = st.chat_input("Command Alpha...")
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"): st.markdown(user_input)
    # Chat logic here...
    
st.caption("Created by Hasith | Bandarawela Central College")
