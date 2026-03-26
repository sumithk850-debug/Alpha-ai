import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
import requests, base64, asyncio
import edge_tts
import urllib.parse
import random  

# -----------------------
# 1. Page Config
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")

st.markdown('<meta name="google-site-verification" content="W6jIGzCkkez2SpjygP6z0dJfinBNALmw2Hv-MkJvFB0" />', unsafe_allow_html=True)

# -----------------------
# 2. Session
# -----------------------
if "messages" not in st.session_state: st.session_state.messages=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None

# -----------------------
# 3. UI
# -----------------------
st.markdown("""
<style>
.premium-banner {padding:15px;background:linear-gradient(90deg,#FFD700,#FF8C00);color:#000;border-radius:15px;text-align:center;font-weight:bold;margin-bottom:20px;font-size:22px;}
.stChatMessage {border-radius: 15px;}
div.stButton > button {background:#1e1e1e;color:#FFD700;border-radius:12px;height:45px;font-weight:bold;border:1px solid #FFD700;}
.lab-box {border:1px solid #333;padding:20px;border-radius:15px;background:#0e1117;margin-bottom:20px;}
</style>
""", unsafe_allow_html=True)

# -----------------------
# 4. Login
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
        else:
            st.error("Access Denied")
    st.stop()

# -----------------------
# 5. API
# -----------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

# -----------------------
# 6. Voice
# -----------------------
async def speak_alpha(text):
    try:
        comm = edge_tts.Communicate(text, "en-US-SteffanNeural")
        audio = b""
        async for chunk in comm.stream():
            if chunk["type"]=="audio":
                audio+=chunk["data"]
        if audio:
            b64 = base64.b64encode(audio).decode()
            st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except:
        pass

# -----------------------
# 7. 🔥 VIDEO FIX FUNCTION
# -----------------------
def generate_video_pollinations(prompt):
    try:
        encoded_p = urllib.parse.quote(prompt)
        seed = random.randint(1, 1000000)

        url = f"https://gen.pollinations.ai/video/{encoded_p}?seed={seed}"

        headers = {
            "Authorization": f"Bearer {POLLINATIONS_KEY}",
            "Accept": "video/mp4"
        }

        response = requests.get(url, headers=headers, timeout=180)

        if response.status_code != 200:
            st.error(f"API Error: {response.status_code}")
            return None

        content_type = response.headers.get("content-type", "")

        if "video" in content_type:
            return response.content
        else:
            st.warning("⚠️ Video failed → showing AI image instead")

            # fallback image
            img_url = f"https://gen.pollinations.ai/image/{encoded_p}?seed={seed}"
            img = requests.get(img_url).content
            st.image(img)
            return None

    except Exception as e:
        st.error(f"Error: {e}")
        return None
import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
import requests, base64, asyncio
import edge_tts
import urllib.parse
import random  

# -----------------------
# 1. Page Config
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")

st.markdown('<meta name="google-site-verification" content="W6jIGzCkkez2SpjygP6z0dJfinBNALmw2Hv-MkJvFB0" />', unsafe_allow_html=True)

# -----------------------
# 2. Session
# -----------------------
if "messages" not in st.session_state: st.session_state.messages=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None

# -----------------------
# 3. UI
# -----------------------
st.markdown("""
<style>
.premium-banner {padding:15px;background:linear-gradient(90deg,#FFD700,#FF8C00);color:#000;border-radius:15px;text-align:center;font-weight:bold;margin-bottom:20px;font-size:22px;}
.stChatMessage {border-radius: 15px;}
div.stButton > button {background:#1e1e1e;color:#FFD700;border-radius:12px;height:45px;font-weight:bold;border:1px solid #FFD700;}
.lab-box {border:1px solid #333;padding:20px;border-radius:15px;background:#0e1117;margin-bottom:20px;}
</style>
""", unsafe_allow_html=True)

# -----------------------
# 4. Login
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
        else:
            st.error("Access Denied")
    st.stop()

# -----------------------
# 5. API
# -----------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

# -----------------------
# 6. Voice
# -----------------------
async def speak_alpha(text):
    try:
        comm = edge_tts.Communicate(text, "en-US-SteffanNeural")
        audio = b""
        async for chunk in comm.stream():
            if chunk["type"]=="audio":
                audio+=chunk["data"]
        if audio:
            b64 = base64.b64encode(audio).decode()
            st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except:
        pass

# -----------------------
# 7. 🔥 VIDEO FIX FUNCTION
# -----------------------
def generate_video_pollinations(prompt):
    try:
        encoded_p = urllib.parse.quote(prompt)
        seed = random.randint(1, 1000000)

        url = f"https://gen.pollinations.ai/video/{encoded_p}?seed={seed}"

        headers = {
            "Authorization": f"Bearer {POLLINATIONS_KEY}",
            "Accept": "video/mp4"
        }

        response = requests.get(url, headers=headers, timeout=180)

        if response.status_code != 200:
            st.error(f"API Error: {response.status_code}")
            return None

        content_type = response.headers.get("content-type", "")

        if "video" in content_type:
            return response.content
        else:
            st.warning("⚠️ Video failed → showing AI image instead")

            # fallback image
            img_url = f"https://gen.pollinations.ai/image/{encoded_p}?seed={seed}"
            img = requests.get(img_url).content
            st.image(img)
            return None

    except Exception as e:
        st.error(f"Error: {e}")
        return None

# -----------------------
# 8. Sidebar
# -----------------------
with st.sidebar:
    st.title("Alpha Control")
    st.markdown(f"Operator: {st.session_state.user_full_name}")
    mode = st.radio("Mode", ["Normal", "Pro"])
    voice_on = st.checkbox("Voice", value=True)

# -----------------------
# 9. Banner
# -----------------------
st.markdown('<div class="premium-banner">⚡ ALPHA AI ULTIMATE</div>', unsafe_allow_html=True)

# -----------------------
# 10. Tabs
# -----------------------
tab_img, tab_vid = st.tabs(["🖼 Image", "🎬 Video"])

# -------- IMAGE --------
with tab_img:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    img_p = st.text_input("Describe image:")
    if st.button("Generate Image"):
        if img_p:
            with st.spinner("Generating..."):
                p = urllib.parse.quote(img_p)
                seed = random.randint(1,1000000)
                url = f"https://gen.pollinations.ai/image/{p}?seed={seed}"
                st.image(url)
    st.markdown('</div>', unsafe_allow_html=True)

# -------- VIDEO --------
with tab_vid:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    vid_p = st.text_input("Describe video:")
    if st.button("Generate Video"):
        if vid_p:
            with st.spinner("Generating video..."):
                vid = generate_video_pollinations(vid_p)
                if vid:
                    st.video(vid)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# 11. Chat
# -----------------------
st.write("### 💬 Chat")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type...")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})

    with st.chat_message("assistant"):
        res_box = st.empty()

        model = "llama-3.3-70b-versatile" if mode=="Normal" else "llama3-70b-8192"

        stream = groq_client.chat.completions.create(
            model=model,
            messages=st.session_state.messages,
            stream=True
        )

        full=""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full+=chunk.choices[0].delta.content
                res_box.markdown(full+"▌")

        res_box.markdown(full)

        if voice_on:
            asyncio.run(speak_alpha(full))

        st.session_state.messages.append({"role":"assistant","content":full})

st.caption("Alpha AI | Created by Hasith")
# -----------------------
# 8. Sidebar
# -----------------------
with st.sidebar:
    st.title("Alpha Control")
    st.markdown(f"Operator: {st.session_state.user_full_name}")
    mode = st.radio("Mode", ["Normal", "Pro"])
    voice_on = st.checkbox("Voice", value=True)

# -----------------------
# 9. Banner
# -----------------------
st.markdown('<div class="premium-banner">⚡ ALPHA AI ULTIMATE</div>', unsafe_allow_html=True)

# -----------------------
# 10. Tabs
# -----------------------
tab_img, tab_vid = st.tabs(["🖼 Image", "🎬 Video"])

# -------- IMAGE --------
with tab_img:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    img_p = st.text_input("Describe image:")
    if st.button("Generate Image"):
        if img_p:
            with st.spinner("Generating..."):
                p = urllib.parse.quote(img_p)
                seed = random.randint(1,1000000)
                url = f"https://gen.pollinations.ai/image/{p}?seed={seed}"
                st.image(url)
    st.markdown('</div>', unsafe_allow_html=True)

# -------- VIDEO --------
with tab_vid:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    vid_p = st.text_input("Describe video:")
    if st.button("Generate Video"):
        if vid_p:
            with st.spinner("Generating video..."):
                vid = generate_video_pollinations(vid_p)
                if vid:
                    st.video(vid)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# 11. Chat
# -----------------------
st.write("### 💬 Chat")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type...")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})

    with st.chat_message("assistant"):
        res_box = st.empty()

        model = "llama-3.3-70b-versatile" if mode=="Normal" else "llama3-70b-8192"

        stream = groq_client.chat.completions.create(
            model=model,
            messages=st.session_state.messages,
            stream=True
        )

        full=""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full+=chunk.choices[0].delta.content
                res_box.markdown(full+"▌")

        res_box.markdown(full)

        if voice_on:
            asyncio.run(speak_alpha(full))

        st.session_state.messages.append({"role":"assistant","content":full})

st.caption("Alpha AI | Created by Hasith")
