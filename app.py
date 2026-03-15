import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
from PyPDF2 import PdfReader
import requests, base64, asyncio, io
import edge_tts
from PIL import Image
import time

# -----------------------
# 1. Page Config & Identity
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
# 3. Custom UI Styling
# -----------------------
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:20px; font-size: 22px; }
    .stChatMessage { border-radius: 15px; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 45px; font-weight: bold; border: 1px solid #FFD700; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# 4. Login System
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#FFD700; font-weight:bold;">Created by Hasith</p>', unsafe_allow_html=True)
    name = st.text_input("Operator Name")
    password = st.text_input("Master Key", type="password")
    if st.button("Initialize Login"):
        if password == "Hasith12378":
            st.session_state.user_full_name = name or "Hasith"
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Key")
    st.stop()

# -----------------------
# 5. API Setup (Groq & HF)
# -----------------------
# Ensure these are in your Streamlit Secrets
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")

groq_client = Groq(api_key=GROQ_API_KEY)
image_client = InferenceClient(token=HF_TOKEN)

# -----------------------
# 6. Helper Functions
# -----------------------
def read_file(upload):
    try:
        if upload.name.endswith(".pdf"):
            reader = PdfReader(upload)
            return "".join([p.extract_text() for p in reader.pages])[:4000]
        return upload.read().decode()
    except: return ""

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

def generate_image(prompt, style):
    model_id = "black-forest-labs/FLUX.1-schnell" 
    full_prompt = f"{prompt}, {style} style, high quality"
    try:
        return image_client.text_to_image(full_prompt, model=model_id)
    except Exception as e:
        st.error(f"Image Error: {e}")
        return None

# -----------------------
# 7. Sidebar
# -----------------------
with st.sidebar:
    st.title("Alpha Control")
    st.markdown(f"**Operator:** {st.session_state.user_full_name}")
    st.divider()
    # ඔබ ඉල්ලූ පරිදි Models වෙන් කළා
    mode = st.radio("Intelligence Mode", ["Normal (Llama 3.3)", "Pro (GPT OSS 120B)"])
    voice_on = st.checkbox("Voice Output", value=True)
    st.divider()
    upload = st.file_uploader("Upload Knowledge (PDF/TXT)")
    if upload:
        text = read_file(upload)
        st.session_state.memory.append(text)
        st.success("Knowledge Added")
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()
    st.write("---")
    st.caption("Developed by Hasith")

# -----------------------
# 8. Main Chat Interface (The Logic Fix)
# -----------------------
st.markdown(f'<div class="premium-banner">⚡ Welcome {st.session_state.user_full_name} | Alpha AI Created by Hasith</div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("State your command...")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"): st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("Alpha is thinking..."):
            res_placeholder = st.empty()
            
            # Model Selection logic
            selected_model = "llama-3.3-70b-versatile" if "Normal" in mode else "openai/gpt-oss-120b"
            
            # Memory integration
            mem_context = "\n".join(st.session_state.memory[-2:])
            sys_msg = f"You are Alpha AI, a heartfelt assistant created by Hasith. Respond warmly in the user's language. Use this context if needed: {mem_context}"

            try:
                chat_completion = groq_client.chat.completions.create(
                    model=selected_model,
                    messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:],
                    temperature=0.7,
                    stream=True
                )
                
                full_res = ""
                for chunk in chat_completion:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        res_placeholder.markdown(full_res + "▌")
                
                res_placeholder.markdown(full_res)
                if voice_on: asyncio.run(speak_alpha(full_res))
                st.session_state.messages.append({"role":"assistant","content":full_res})
            except Exception as e:
                st.error(f"API Error: {e}")

# -----------------------
# 9. Image Generation
# -----------------------
st.write("---")
st.subheader("🖼 AI Image Lab")
with st.expander("Create Visual Data"):
    col1, col2 = st.columns([3, 1])
    with col1:
        img_p = st.text_input("Image Description")
    with col2:
        img_s = st.selectbox("Style", ["Realistic", "Cyberpunk", "Anime", "Cinematic"])
    
    if st.button("Generate Image"):
        if img_p:
            with st.spinner("Alpha is generating..."):
                img = generate_image(img_p, img_s)
                if img:
                    st.image(img)
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button("Download Image", buf.getvalue(), "alpha.png", "image/png")
