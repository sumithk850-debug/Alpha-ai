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
# 3. Premium UI Styling (Original Gold Theme)
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
        else: st.error("Access Denied")
    st.stop()

# -----------------------
# 5. API Setup
# -----------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

# -----------------------
# 6. Helper Functions
# -----------------------
def generate_music_hf(prompt):
    try:
        API_URL = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=150)
        if response.status_code == 200: return response.content
        elif response.status_code == 503: return "loading"
        else: return None
    except: return None

# -----------------------
# 7. Sidebar Control
# -----------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluent/100/000000/artificial-intelligence.png", width=70)
    st.title("Alpha Control")
    st.markdown(f"**Operator:** {st.session_state.user_full_name}")
    st.divider()
    mode = st.radio("Intelligence Level", ["Normal", "Pro"])
    voice_on = st.checkbox("Voice Output", value=True)
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# -----------------------
# 8. AI Multimodal Labs
# -----------------------
tab_img, tab_vid, tab_music = st.tabs(["🖼 Image Lab", "🎬 Cinema Lab", "🎵 Music Studio"])

# --- IMAGE LAB (Cover Photos) ---
with tab_img:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    img_p = col1.text_input("Describe image/cover photo:", key="img_p")
    img_model = st.selectbox("Model:", ["flux", "turbo", "zimage"], key="img_m")
    if col2.button("Generate Image"):
        if img_p:
            with st.spinner("Alpha is painting..."):
                seed = random.randint(1, 999999)
                url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(img_p)}?width=1024&height=1024&seed={seed}&model={img_model}&nologo=true"
                st.image(url, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- CINEMA LAB (Video) ---
with tab_vid:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    vid_p = col1.text_input("Describe video scene:", key="vid_p")
    if col2.button("Generate Video"):
        if vid_p:
            with st.spinner("Alpha is directing cinema... (LTX-2)"):
                v_url = f"https://gen.pollinations.ai/video/{urllib.parse.quote(vid_p)}?model=ltx-2&nologo=true"
                headers = {"Authorization": f"Bearer {POLLINATIONS_KEY}"} if POLLINATIONS_KEY else {}
                res = requests.get(v_url, headers=headers, timeout=300)
                if res.status_code == 200:
                    st.video(res.content)
                else:
                    st.error("Engine busy or insufficient balance.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- MUSIC STUDIO (Free Hugging Face Engine) ---
with tab_music:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    music_p = st.text_input("Describe music (e.g., Epic cinematic drums):", key="mus_p")
    if st.button("Compose Music 🎶"):
        if music_p:
            with st.spinner("Alpha is composing... This takes about 1 minute."):
                for _ in range(3):
                    data = generate_music_hf(music_p)
                    if data == "loading":
                        time.sleep(20)
                        continue
                    elif data:
                        st.audio(data, format="audio/wav")
                        st.download_button("Download mp3", data, "alpha_track.mp3")
                        break
                else: st.warning("Server busy. Try again in a moment.")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# 9. Conversation Chat
# -----------------------
st.write("### 💬 Conversation")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

user_input = st.chat_input("State your command, Master...")
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"): st.markdown(user_input)
    with st.chat_message("assistant"):
        res = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are Alpha AI, created by Hasith. You are wise and helpful."}] + st.session_state.messages[-10:]
        )
        msg = res.choices[0].message.content
        st.markdown(msg)
        st.session_state.messages.append({"role":"assistant","content":msg})

st.markdown("---")
st.caption("Alpha AI Project | Bandarawela Central College | Created by Hasith")
