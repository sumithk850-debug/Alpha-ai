import streamlit as st
from huggingface_hub import InferenceClient
from PyPDF2 import PdfReader
import requests, base64, asyncio, io
import edge_tts
from PIL import Image
import time

# -----------------------
# 1. Page Config (Branding by Hasith)
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
# 3. Custom UI Styling (Created by Hasith)
# -----------------------
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:20px; font-size: 22px; }
    .stChatMessage { border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# 4. Login System
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#FFD700;">Created by Hasith</p>', unsafe_allow_html=True)
    name = st.text_input("Operator Name")
    password = st.text_input("Master Key", type="password")
    if st.button("Initialize Login"):
        if password == "Hasith12378":
            st.session_state.user_full_name = name or "Hasith"
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Access Denied: Invalid Master Key")
    st.stop()

# -----------------------
# 5. API Setup (Hugging Face)
# -----------------------
HF_TOKEN = st.secrets.get("HF_TOKEN")
image_client = InferenceClient(token=HF_TOKEN)

# -----------------------
# 6. Helper Functions
# -----------------------
def read_file(upload):
    try:
        if upload.name.endswith(".pdf"):
            reader = PdfReader(upload)
            text = "".join([p.extract_text() for p in reader.pages])
            return text[:4000]
        else:
            return upload.read().decode()
    except: return "Error reading file."

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
    # වඩාත් බලවත් FLUX මාදිලිය භාවිතා කර ඇත
    model_id = "black-forest-labs/FLUX.1-schnell" 
    full_prompt = f"{prompt}, {style} style, high resolution, 4k"
    try:
        # පින්තූරය Bytes ලෙස ලබා ගෙන PIL හරහා විවෘත කිරීම
        image_data = image_client.text_to_image(full_prompt, model=model_id)
        return image_data
    except Exception as e:
        st.error(f"HF Error: {e}")
        return None

# -----------------------
# 7. Sidebar
# -----------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluent/100/000000/artificial-intelligence.png", width=80)
    st.title("Alpha Control")
    st.markdown(f"**Operator:** {st.session_state.user_full_name}")
    st.write("---")
    mode = st.radio("Intelligence Level", ["Normal (Llama 3.3)", "Pro (GPT OSS 120B)"])
    
    st.subheader("Capabilities")
    voice_on = st.checkbox("Voice Output", value=True)
    
    st.divider()
    upload = st.file_uploader("Upload Data (PDF/TXT)")
    if upload:
        text = read_file(upload)
        st.session_state.memory.append(text)
        st.success("Memory Updated")
    
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()
    st.write("---")
    st.caption("Created by Hasith")

# -----------------------
# 8. Main Chat Interface
# -----------------------
st.markdown(f'<div class="premium-banner">⚡ Welcome {st.session_state.user_full_name} | Alpha AI Created by Hasith</div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("State your command, Master...")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"): st.markdown(user_input)
    
    with st.chat_message("assistant"):
        # Alpha is Thinking Spinner
        with st.spinner("Alpha is thinking..."):
            # මෙහිදී ඔබේ AI Model එකට අදාළ සැබෑ API Call එක ලබා දිය හැක
            time.sleep(1) # Simulation
            answer = f"I am Alpha, your AI assistant created by Hasith. You asked: '{user_input}'. How can I further assist you today?"
            st.markdown(answer)
            if voice_on: asyncio.run(speak_alpha(answer))
            
    st.session_state.messages.append({"role":"assistant","content":answer})

# -----------------------
# 9. Enhanced Image Generator
# -----------------------
st.write("---")
st.subheader("🖼 AI Image Generation Lab")
with st.expander("Create Visuals"):
    col1, col2 = st.columns([3, 1])
    with col1:
        img_prompt = st.text_input("Describe the visual...")
    with col2:
        style = st.selectbox("Style", ["Realistic", "Cyberpunk", "Anime", "Cinematic"])
    
    if st.button("Execute Generation"):
        if img_prompt:
            with st.spinner("Alpha is generating visual data..."):
                img = generate_image(img_prompt, style)
                if img:
                    st.image(img, caption=f"Alpha Creation: {img_prompt}")
                    # Download Link
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    st.markdown(f'<a href="data:image/png;base64,{img_str}" download="alpha_gen.png" style="text-decoration:none; background-color:#FFD700; color:black; padding:8px; border-radius:5px;">Download Image</a>', unsafe_allow_html=True)
        else:
            st.warning("Please provide a description.")
