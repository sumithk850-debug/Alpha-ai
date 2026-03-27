import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
import requests, base64, asyncio, io, json
import edge_tts
from PIL import Image
import time, urllib.parse, random

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")

# -----------------------
# SESSION STATE
# -----------------------
if "messages" not in st.session_state: st.session_state.messages=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None
if "memory" not in st.session_state: st.session_state.memory={}

# -----------------------
# LOGIN
# -----------------------
if not st.session_state.logged_in:
    st.markdown("## ⚡ ALPHA CORE LOGIN")
    name = st.text_input("Operator Name")
    password = st.text_input("Master Key", type="password")
    if st.button("Initialize"):
        if password == "Hasith12378":
            st.session_state.logged_in=True
            st.session_state.user_full_name=name or "Operator"
            st.rerun()
        else:
            st.error("Access Denied")
    st.stop()

# -----------------------
# API
# -----------------------
groq_client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY", "")

# -----------------------
# SIDEBAR (ALL CONTROLS HERE 🔥)
# -----------------------
with st.sidebar:
    st.title("⚡ Alpha Control Panel")

    st.write("### 👤 User")
    st.write(st.session_state.user_full_name)

    st.divider()

    mode = st.selectbox("🧠 Model", ["Fast (LLaMA)", "Smart (Pro)"])
    agent = st.selectbox("🤖 AI Mode", ["General", "Coder", "Teacher", "Business"])

    personality = st.selectbox("🎭 Personality", ["Friendly", "Serious", "Funny", "Motivational"])

    voice_on = st.toggle("🔊 Voice Output", True)

    st.divider()

    st.write("### 🎨 Image Settings")
    img_style = st.selectbox("Style", ["Realistic", "Anime", "Cyberpunk", "Fantasy"])

    st.write("### 🎬 Video Settings")
    vid_duration = st.slider("Duration", 3, 10, 5)

    st.divider()

    if st.button("💾 Save Chat"):
        with open("chat.json", "w") as f:
            json.dump(st.session_state.messages, f)

    if st.button("📂 Load Chat"):
        try:
            with open("chat.json", "r") as f:
                st.session_state.messages=json.load(f)
        except:
            st.warning("No saved chat")

    if st.button("🚪 Logout"):
        st.session_state.logged_in=False
        st.rerun()

# -----------------------
# VOICE FUNCTION
# -----------------------
async def speak(text):
    try:
        tts = edge_tts.Communicate(text, "en-US-SteffanNeural")
        audio=b""
        async for chunk in tts.stream():
            if chunk["type"]=="audio":
                audio+=chunk["data"]
        b64=base64.b64encode(audio).decode()
        st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except:
        pass

# -----------------------
# TABS
# -----------------------
tab1, tab2 = st.tabs(["🖼 Image", "🎬 Video"])

# -----------------------
# IMAGE
# -----------------------
with tab1:
    prompt = st.text_input("Describe Image")

    if st.button("Generate Image"):
        if prompt:
            final_prompt = f"{prompt}, {img_style} style, ultra detailed"
            encoded = urllib.parse.quote(final_prompt)
            seed = random.randint(1,999999)

            url = f"https://gen.pollinations.ai/image/{encoded}?seed={seed}"
            res = requests.get(url)

            if res.status_code==200:
                st.image(res.content)
                st.download_button("Download", res.content, "image.png")

# -----------------------
# VIDEO
# -----------------------
with tab2:
    vprompt = st.text_input("Describe Video")

    if st.button("Generate Video"):
        if vprompt:
            encoded = urllib.parse.quote(vprompt)
            url = f"https://gen.pollinations.ai/video/{encoded}?duration={vid_duration}"
            res = requests.get(url)

            if res.status_code==200:
                st.video(res.content)
                st.download_button("Download", res.content, "video.mp4")

# -----------------------
# CHAT
# -----------------------
st.write("## 💬 Alpha Chat")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type here...")

if user_input:

    # MEMORY SAVE
    if "my name is" in user_input.lower():
        st.session_state.memory["name"]=user_input.split("is")[-1].strip()

    st.session_state.messages.append({"role":"user","content":user_input})

    with st.chat_message("assistant"):
        placeholder = st.empty()

        sys_msg="You are Alpha AI."

        # AGENTS
        if agent=="Coder":
            sys_msg="Expert programmer."
        elif agent=="Teacher":
            sys_msg="Explain simply."
        elif agent=="Business":
            sys_msg="Business expert."

        # PERSONALITY
        if personality=="Funny":
            sys_msg+=" Be funny."
        elif personality=="Serious":
            sys_msg+=" Be serious."
        elif personality=="Motivational":
            sys_msg+=" Be motivational."

        # MEMORY USE
        if "name" in st.session_state.memory:
            sys_msg += f" User name is {st.session_state.memory['name']}."

        model = "llama3-70b-8192" if "Pro" in mode else "llama-3.3-70b-versatile"

        stream = groq_client.chat.completions.create(
            model=model,
            messages=[{"role":"system","content":sys_msg}] + st.session_state.messages,
            stream=True
        )

        full=""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full+=chunk.choices[0].delta.content
                placeholder.markdown(full+"▌")

        placeholder.markdown(full)

        if voice_on:
            asyncio.run(speak(full))

        st.session_state.messages.append({"role":"assistant","content":full})
