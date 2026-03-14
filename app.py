import streamlit as st
from groq import Groq
import time, base64, asyncio, requests, webbrowser
import edge_tts
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from email_validator import validate_email

# -----------------------
# Page Config
# -----------------------

st.set_page_config(page_title="Alpha AI | Jarvis", page_icon="⚡", layout="wide")

# -----------------------
# Session State
# -----------------------

if "messages" not in st.session_state:
    st.session_state.messages=[]

if "memory" not in st.session_state:
    st.session_state.memory=[]

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

if "user_full_name" not in st.session_state:
    st.session_state.user_full_name=None


# -----------------------
# Login
# -----------------------

if not st.session_state.logged_in:

    st.title("⚡ Alpha AI Login")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1,col2 = st.columns(2)

    with col1:
        if st.button("Register"):
            if name and email and password:
                try:
                    validate_email(email)
                    st.session_state.logged_in=True
                    st.session_state.user_full_name=name
                    st.rerun()
                except:
                    st.error("Invalid Email")

    with col2:
        if st.button("Login"):
            if password=="Hasith12378":
                st.session_state.logged_in=True
                st.session_state.user_full_name=name
                st.rerun()

    st.stop()


# -----------------------
# Voice AI
# -----------------------

async def speak_alpha(text):

    voice="en-US-SteffanNeural"

    comm=edge_tts.Communicate(text,voice)

    audio=b""

    async for chunk in comm.stream():
        if chunk["type"]=="audio":
            audio+=chunk["data"]

    b64=base64.b64encode(audio).decode()

    st.markdown(
        f'<audio autoplay src="data:audio/mp3;base64,{b64}">',
        unsafe_allow_html=True
    )


# -----------------------
# Internet Search
# -----------------------

def internet_search(query):

    url=f"https://www.google.com/search?q={query}"

    headers={"User-Agent":"Mozilla/5.0"}

    r=requests.get(url,headers=headers)

    soup=BeautifulSoup(r.text,"html.parser")

    results=[g.text for g in soup.select("div.BNeawe")[:5]]

    return "\n".join(results)


# -----------------------
# File Reader
# -----------------------

def read_file(upload):

    if upload.name.endswith(".pdf"):

        reader=PdfReader(upload)

        text="".join([p.extract_text() for p in reader.pages])

        return text[:4000]

    else:

        return upload.read().decode()


# -----------------------
# Image Generation
# -----------------------

def generate_image(prompt):

    url = "https://api.stability.ai/v2beta/stable-image/generate/core"

    headers = {
        "Authorization": f"Bearer {st.secrets['STABILITY_API_KEY']}",
        "Accept": "image/*"
    }

    files = {
        "prompt": (None, prompt),
        "output_format": (None, "png")
    }

    response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        return response.content
    else:
        st.error(f"API Error: {response.text}")
        return None


# -----------------------
# AI Client
# -----------------------

client=Groq(api_key=st.secrets["GROQ_API_KEY"])

def ask_ai(prompt,mode):

    memory="\n".join(st.session_state.memory[-5:])

    if mode=="Normal":
        model="llama-3.3-70b-versatile"
    else:
        model="openai/gpt-oss-120b"

    messages=[
        {"role":"system","content":"You are Alpha AI created by Hasith."},
        {"role":"system","content":memory},
        {"role":"user","content":prompt}
    ]

    res=client.chat.completions.create(
        model=model,
        messages=messages
    )

    return res.choices[0].message.content


# -----------------------
# Sidebar
# -----------------------

with st.sidebar:

    st.header("⚡ Alpha Control Panel")

    st.write(f"Operator: **{st.session_state.user_full_name}**")

    power=st.slider("AI Power Level",0,1,0)

    if power==0:
        mode="Normal"
        st.caption("⚡ LLaMA Fast Mode")
    else:
        mode="Pro"
        st.caption("🚀 GPT Ultra Mode")

    voice_mode=st.checkbox("Voice Chat")

    internet_mode=st.checkbox("Internet Search")

    uploaded=st.file_uploader("Upload File")

    if uploaded:
        text=read_file(uploaded)
        st.session_state.memory.append(text)
        st.success("File loaded into memory")

    if st.button("Clear Memory"):
        st.session_state.memory=[]

    if st.button("Logout"):
        st.session_state.logged_in=False
        st.rerun()

    st.divider()

    # IMAGE GENERATOR

    st.subheader("🖼 Image Generator")

    img_prompt=st.text_input("Describe image")

    if st.button("Generate Image"):

        if img_prompt.strip()=="":

            st.warning("Enter image description")

        else:

            with st.spinner("Generating image..."):

                img=generate_image(img_prompt)

                if img:
                    st.image(img)
                else:
                    st.error("Image generation failed")

    st.divider()

    # VIDEO GENERATOR

    st.subheader("🎬 Video Generator")

    video_prompt=st.text_input("Describe video")

    if st.button("Generate Video"):
        st.info("Video generation coming soon")


# -----------------------
# Main Chat
# -----------------------

st.title(f"Welcome {st.session_state.user_full_name}")

st.write("Alpha AI ready...")

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])


user_input=st.chat_input("Ask Alpha...")

if user_input:

    st.session_state.messages.append({"role":"user","content":user_input})

    with st.chat_message("user"):

        st.markdown(user_input)

    with st.chat_message("assistant"):

        if internet_mode:

            prompt=user_input+"\n\nInternet Data:\n"+internet_search(user_input)

        else:

            prompt=user_input

        with st.spinner("Thinking..."):

            answer=ask_ai(prompt,mode)

        st.markdown(answer)

        if voice_mode:

            asyncio.run(speak_alpha(answer))

        st.session_state.messages.append({"role":"assistant","content":answer})
