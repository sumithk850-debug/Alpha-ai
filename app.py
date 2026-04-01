import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
import requests, base64, asyncio, io, json, datetime
import edge_tts
from PIL import Image
import time
import urllib.parse
import random
from duckduckgo_search import DDGS 
import extra_streamlit_components as stx

# -----------------------
# 1. Page Config
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")
st.markdown('<meta name="google-site-verification" content="W6jIGzCkkez2SpjygP6z0dJfinBNALmw2Hv-MkJvFB0" />', unsafe_allow_html=True)

# -----------------------
# 2. Cookie Management (අවුරුද්දක් මතක තබා ගැනීමට)
# -----------------------
cookie_manager = stx.CookieManager()
saved_user_email = cookie_manager.get(cookie="alpha_user_persistence")

if "messages" not in st.session_state: st.session_state.messages=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None

# Auto-Login Logic
if saved_user_email and not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.user_full_name = saved_user_email

# -----------------------
# 3. Custom UI Styling
# -----------------------
st.markdown("""
<style>  
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:20px; font-size: 22px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }  
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 45px; font-weight: bold; border: 1px solid #FFD700; transition: 0.3s; }  
    div.stButton > button:hover { background-color: #FFD700; color: #000; }  
    .lab-box { border: 1px solid #333; padding: 20px; border-radius: 15px; background: #0e1117; margin-bottom: 20px; }  
</style>  """, unsafe_allow_html=True)

# -----------------------
# 4. Login System
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#FFD700; font-weight:bold;">Developed by Hasith</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user_email = st.text_input("Operator Email / Name")
        password = st.text_input("Master Key", type="password")
        
        if st.button("Initialize Alpha"):
            if password == "Hasith12378":
                st.session_state.user_full_name = user_email or "Hasith"
                st.session_state.logged_in = True
                
                # Cookie එක අවුරුද්දකට සෙට් කිරීම
                expire_date = datetime.datetime.now() + datetime.timedelta(days=365)
                cookie_manager.set("alpha_user_persistence", user_email, expires_at=expire_date)
                
                st.success("Access Granted!")
                time.sleep(1)
                st.rerun()
            else: 
                st.error("Access Denied: Invalid Master Key")
    st.stop()

# -----------------------
# 5. API Setup
# -----------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY", "sk_Z0oEnm05szbphnbZ9ClRCukKV2HyDMH5")

groq_client = Groq(api_key=GROQ_API_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

# -----------------------
# 6. Helper Functions
# -----------------------
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

def generate_video_robust(prompt):
    models = ["guoyww/AnimateDiff", "cerspense/zeroscope_v2_576w"]
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    for model_id in models:
        try:
            API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
            if response.status_code == 200: return response.content
        except: continue
    return None

# -----------------------
# 7. Sidebar
# -----------------------
with st.sidebar:
    st.title("Alpha Control")
    st.markdown(f"Operator: **{st.session_state.user_full_name}**")
    st.divider()
    st.metric(label="Active Alpha Operators", value="10+") 
    mode = st.radio("Intelligence Level", ["Normal (Llama 3.3 70B)", "Pro (Llama 3.1 70B)"])
    voice_on = st.checkbox("Voice Output", value=True)
    if st.button("Log Out"):
        cookie_manager.delete("alpha_user_persistence")
        st.session_state.logged_in = False
        st.rerun()
    st.caption("Created by Hasith | Bandarawela Central College")

st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# -----------------------
# 8. Labs
# -----------------------
tab_img, tab_vid = st.tabs(["🖼 Image Lab", "🎬 Cinema Lab"])

with tab_img:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    img_p = col1.text_input("Describe image:", key="img_prompt")
    img_model = st.selectbox("Style:", ["flux", "turbo", "zimage"], key="img_model_select")  
    if col2.button("Generate Photo"):  
        if img_p:  
            with st.spinner("Alpha is painting..."):  
                try:  
                    seed = random.randint(1, 1000000)  
                    encoded_p = urllib.parse.quote(img_p)
                    # Pollinations API එකට headers අවශ්‍ය නැහැ
                    url = f"https://gen.pollinations.ai/image/{encoded_p}?width=1024&height=1024&seed={seed}&model={img_model}&nologo=true"  
                    response = requests.get(url, timeout=60)
                    if response.status_code == 200:
                        st.image(response.content, use_container_width=True)
                        st.download_button("Download 📥", response.content, f"alpha_{seed}.png", "image/png")
                    else: st.error("Pollinations API Error")
                except Exception as e: st.error(f"Error: {e}")  
    st.markdown('</div>', unsafe_allow_html=True)

with tab_vid:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    vid_p = st.text_input("Describe video scene:", key="vid_prompt")
    if st.button("Generate Video"):
        if vid_p:
            with st.spinner("Directing..."):
                vid_data = generate_video_robust(vid_p)
                if vid_data: st.video(vid_data)
                else: st.error("Video core busy.")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# 9. Chat
# -----------------------
st.write("### 💬 Conversation")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

user_input = st.chat_input("Command me...")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"): st.markdown(user_input)
    
    with st.chat_message("assistant"):
        res_placeholder = st.empty()
        sys_msg = f"Your name is Alpha AI. Created by Hasith from Bandarawela Central College."
        
        try:
            selected_model = "llama-3.3-70b-versatile" if "Normal" in mode else "llama-3.1-70b-versatile"
            stream = groq_client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:],
                stream=True
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

st.markdown("---")
st.caption("Alpha AI Project | Created by Hasith")
