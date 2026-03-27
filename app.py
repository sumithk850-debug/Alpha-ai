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
# 1. Page Config & Identity (Hasith)
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")

# --- GOOGLE VERIFICATION ---
st.markdown('<meta name="google-site-verification" content="W6jIGzCkkez2SpjygP6z0dJfinBNALmw2Hv-MkJvFB0" />', unsafe_allow_html=True)

# -----------------------
# 2. Session State
# -----------------------
if "messages" not in st.session_state: st.session_state.messages=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None

# -----------------------
# 3. Premium UI Styling
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
# 6. Audio/Music Function (Based on your Documentation)
# -----------------------
def generate_audio_pollinations(text):
    try:
        encoded_text = urllib.parse.quote(text)
        # GET /audio/{text} endpoint එක භාවිතා කිරීම
        url = f"https://gen.pollinations.ai/audio/{encoded_text}"
        headers = {"Authorization": f"Bearer {POLLINATIONS_KEY}"}
        
        response = requests.get(url, headers=headers, timeout=120)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except:
        return None

# -----------------------
# 7. Sidebar
# -----------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluent/100/000000/artificial-intelligence.png", width=70)
    st.title("Alpha Control")
    st.markdown(f"**Operator:** {st.session_state.user_full_name}")
    st.divider()
    mode = st.radio("Intelligence Level", ["Normal (Llama 3.3 Fast)", "Pro (GPT OSS 120B)"])
    voice_on = st.checkbox("Voice Output", value=True)
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()
    st.caption("Created by Hasith | Bandarawela Central College")

st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# -----------------------
# 8. Multi-Modal Labs
# -----------------------
tab_img, tab_vid, tab_music = st.tabs(["🖼 Image Generation Lab", "🎬 Cinema Lab (AI Video)", "🎵 Music Studio"])

# --- IMAGE LAB ---
with tab_img:
    with st.container():
        st.markdown('<div class="lab-box">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        img_p = col1.text_input("Describe image:", key="img_prompt")
        img_model = st.selectbox("Intelligence Mode:", ["flux", "turbo", "zimage", "p-image"], key="img_model_select")
        if col2.button("Generate Photo"):
            if img_p:
                with st.spinner("Alpha is painting..."):
                    img_url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(img_p)}?width=1024&height=1024&model={img_model}&nologo=true"
                    st.image(img_url, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- VIDEO LAB (LTX-2) ---
with tab_vid:
    with st.container():
        st.markdown('<div class="lab-box">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        vid_p = col1.text_input("Describe video scene:", key="vid_prompt")
        if col2.button("Generate Video"):
            if vid_p:
                with st.spinner("Alpha is directing cinema..."):
                    v_url = f"https://gen.pollinations.ai/video/{urllib.parse.quote(vid_p)}?model=ltx-2&nologo=true"
                    headers = {"Authorization": f"Bearer {POLLINATIONS_KEY}"}
                    res = requests.get(v_url, headers=headers, timeout=300)
                    if res.status_code == 200:
                        st.video(res.content)
                    else:
                        st.error("Insufficient Pollen Balance or API Busy.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- MUSIC STUDIO (Based on your specific request) ---
with tab_music:
    with st.container():
        st.markdown('<div class="lab-box">', unsafe_allow_html=True)
        music_text = st.text_input("Describe the Music or Text to Audio (e.g., 'Techno beat' or 'Hello Hasith'):")
        if st.button("Compose/Speak 🎶"):
            if music_text:
                with st.spinner("Alpha is generating audio..."):
                    audio_data = generate_audio_pollinations(music_text)
                    if audio_data:
                        st.audio(audio_data, format="audio/mp3")
                        st.download_button("Download Audio 📥", audio_data, "alpha_audio.mp3")
                    else:
                        st.warning("Audio Engine busy. Please check your Pollen balance.")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# 9. Conversation
# -----------------------
st.write("### 💬 Heartfelt Conversation")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

user_input = st.chat_input("State your command, Master...")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"): st.markdown(user_input)
    with st.chat_message("assistant"):
        res_placeholder = st.empty()
        selected_model = "llama-3.3-70b-versatile" if "Normal" in mode else "llama3-70b-8192" 
        try:
            stream = groq_client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "system", "content": "You are Alpha AI, created by Hasith. You are helpful and wise."}] + st.session_state.messages,
                stream=True
            )
            full_res = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_placeholder.markdown(full_res + "▌")
            res_placeholder.markdown(full_res)
            st.session_state.messages.append({"role":"assistant","content":full_res})
        except Exception as e: st.error(f"Error: {e}")

st.markdown("---")
st.caption("Alpha AI Project | Bandarawela Central College | Created by Hasith")
