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

# --- GOOGLE VERIFICATION TAG ---
st.markdown('<meta name="google-site-verification" content="W6jIGzCkkez2SpjygP6z0dJfinBNALmw2Hv-MkJvFB0" />', unsafe_allow_html=True)

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
        else: st.error("Access Denied: Invalid Master Key")
    st.stop()

# -----------------------
# 5. API Setup (Using Secrets)
# -----------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

# -----------------------
# 6. Audio/Music Generation Function
# -----------------------
def generate_audio_pollinations(prompt):
    try:
        encoded_p = urllib.parse.quote(prompt)
        # Using the GET /audio/{text} endpoint as requested
        # 'elevenlabs-music' is inferred from your provided image labels
        url = f"https://gen.pollinations.ai/audio/{encoded_p}?model=elevenlabs-music"
        
        headers = {
            "Authorization": f"Bearer {POLLINATIONS_KEY}"
        }
        
        response = requests.get(url, headers=headers, timeout=150)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception as e:
        return None

# -----------------------
# 7. Sidebar Control
# -----------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluent/100/000000/artificial-intelligence.png", width=70)
    st.title("Alpha Control")
    st.markdown(f"**Operator:** {st.session_state.user_full_name}")
    st.divider()
    mode = st.radio("Intelligence Level", ["Normal (Llama 3.3 Fast)", "Pro (GPT OSS 120B)"])
    voice_on = st.checkbox("Voice Output", value=True)
    st.divider()
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()
    st.write("---")
    st.caption("Created by Hasith | Bandarawela Central College")

st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# -----------------------
# 8. AI Multimodal Labs
# -----------------------
tab_img, tab_vid, tab_music = st.tabs(["🖼 Image Lab", "🎬 Cinema Lab (Video)", "🎵 Music Studio"])

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
                    img_url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(img_p)}?width=1024&height=1024&seed={random.randint(1,1000)}&model={img_model}&nologo=true"
                    st.image(img_url, caption=f"Created for {st.session_state.user_full_name}", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- VIDEO LAB (LTX-2) ---
with tab_vid:
    with st.container():
        st.markdown('<div class="lab-box">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        vid_p = col1.text_input("Describe video scene:", key="vid_prompt")
        if col2.button("Generate Video"):
            if vid_p:
                with st.spinner("Alpha is directing cinema via LTX-2 Engine..."):
                    v_url = f"https://gen.pollinations.ai/video/{urllib.parse.quote(vid_p)}?model=ltx-2&nologo=true"
                    headers = {"Authorization": f"Bearer {POLLINATIONS_KEY}"}
                    res = requests.get(v_url, headers=headers, timeout=300)
                    if res.status_code == 200:
                        st.video(res.content)
                    else:
                        st.error("Error: Check Pollen Balance or API Status.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- MUSIC STUDIO (GET /audio/ Request) ---
with tab_music:
    with st.container():
        st.markdown('<div class="lab-box">', unsafe_allow_html=True)
        music_text = st.text_input("Describe the music (e.g. 'Epic cinematic drums' or 'Lo-fi beat'):")
        if st.button("Generate Music 🎶"):
            if music_text:
                with st.spinner("Alpha is composing audio via ElevenLabs Music..."):
                    audio_data = generate_audio_pollinations(music_text)
                    if audio_data:
                        st.audio(audio_data, format="audio/mp3")
                        st.download_button("Download Audio 📥", audio_data, "alpha_audio.mp3")
                    else:
                        st.warning("Audio generation failed. Please check your Pollen balance.")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# 9. Hybrid Intelligence Chat
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
                messages=[{"role": "system", "content": "You are Alpha AI, created by Hasith. Provide wise and helpful responses."}] + st.session_state.messages[-10:],
                stream=True
            )
            full_res = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_placeholder.markdown(full_res + "▌")
            res_placeholder.markdown(full_res)
            st.session_state.messages.append({"role":"assistant","content":full_res})
        except Exception as e: st.error(f"Chat Error: {e}")

st.markdown("---")
st.caption("Alpha AI Project | Bandarawela Central College | Created by Hasith")
