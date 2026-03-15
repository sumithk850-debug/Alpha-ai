import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
from gradio_client import Client as GradioClient
from PyPDF2 import PdfReader
import requests, base64, asyncio, io
import edge_tts
from PIL import Image
import time

# -----------------------
# 1. Page Config & Identity (Hasith's Authority)
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")

# -----------------------
# 2. Session State Init
# -----------------------
if "messages" not in st.session_state: st.session_state.messages=[]
if "memory" not in st.session_state: st.session_state.memory=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None

# -----------------------
# 3. Custom UI Styling (Hasith's Original Style)
# -----------------------
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:20px; font-size: 22px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
    .stChatMessage { border-radius: 15px; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 45px; font-weight: bold; border: 1px solid #FFD700; transition: 0.3s; }
    div.stButton > button:hover { background-color: #FFD700; color: #000; }
    .lab-box { border: 1px solid #333; padding: 20px; border-radius: 15px; background: #0e1117; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# 4. Login System (Hasith12378)
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#FFD700; font-weight:bold;">Created by Hasith</p>', unsafe_allow_html=True)
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

groq_client = Groq(api_key=GROQ_API_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

# -----------------------
# 6. Advanced Video Streaming (Bypass Busy Error)
# -----------------------
def generate_video_streaming(prompt):
    try:
        # සෘජුවම Hugging Face Space එකකට සම්බන්ධ වීම
        client = GradioClient("guoyww/AnimateDiff")
        result = client.predict(
            prompt=prompt,
            n_prompt="bad quality, blurry, low resolution",
            api_name="/predict"
        )
        # ලැබෙන වීඩියෝ ගොනුව කියවා Bytes ලබා ගැනීම
        with open(result, "rb") as f:
            return f.read()
    except Exception as e:
        return None

async def speak_alpha(text):
    try:
        comm = edge_tts.Communicate(text, "en-US-SteffanNeural")
        audio = b""
        async for chunk in comm.stream():
            if chunk["type"]=="audio": audio+=chunk["data"]
        if audio:
            b64 = base64.b64encode(audio).decode()
            st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# -----------------------
# 7. Sidebar
# -----------------------
with st.sidebar:
    st.title("Alpha Control")
    st.markdown(f"**Operator:** {st.session_state.user_full_name}")
    st.divider()
    mode = st.radio("Intelligence Level", ["Normal (Llama 3.3 Fast)", "Pro (GPT OSS 120B)"])
    voice_on = st.checkbox("Voice Output", value=True)
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()
    st.write("---")
    st.caption("Created by Hasith")

st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# -----------------------
# 8. AI Multimodal Labs
# -----------------------
tab_img, tab_vid = st.tabs(["🖼 Image Lab", "🎬 Cinema Lab (Video)"])

with tab_img:
    img_p = st.text_input("Describe Image", key="img_prompt")
    if st.button("Generate Photo"):
        with st.spinner("Alpha is painting..."):
            img = hf_client.text_to_image(img_p, model="black-forest-labs/FLUX.1-schnell")
            st.image(img)

with tab_vid:
    vid_p = st.text_input("Describe Video Scene", key="vid_prompt")
    if st.button("Generate Video"):
        with st.spinner("Alpha is establishing a streaming link to Cinema Lab... 🎬"):
            vid_data = generate_video_streaming(vid_p)
            if vid_data:
                st.video(vid_data)
                st.download_button("Download Video", vid_data, "alpha_video.mp4")
            else:
                st.error("Streaming failed. The Cinema Lab Space might be sleeping. Please try again.")

# -----------------------
# 9. Hybrid Intelligence Chat
# -----------------------
st.write("### 💬 Heartfelt Conversation")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

user_input = st.chat_input("State your command...")
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"): st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("Alpha is thinking..."):
            res_placeholder = st.empty()
            selected_model = "llama-3.3-70b-versatile" if "Normal" in mode else "openai/gpt-oss-120b"
            sys_msg = f"You are Alpha AI, a heartfelt assistant created by Hasith. Respond warmly in the user's language."
            try:
                stream = groq_client.chat.completions.create(
                    model=selected_model,
                    messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:],
                    temperature=0.7, stream=True
                )
                full_res = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        res_placeholder.markdown(full_res + "▌")
                res_placeholder.markdown(full_res)
                if voice_on: asyncio.run(speak_alpha(full_res))
                st.session_state.messages.append({"role":"assistant","content":full_res})
            except Exception as e: st.error(f"Error: {e}")
