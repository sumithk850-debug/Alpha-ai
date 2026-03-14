import streamlit as st
from groq import Groq
import time, base64, asyncio, requests, webbrowser
import edge_tts
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup

# -----------------------
# Page Config
# -----------------------
st.set_page_config(page_title="Alpha AI | Jarvis", page_icon="⚡", layout="wide")

# -----------------------
# Session State
# -----------------------
if "messages" not in st.session_state: st.session_state.messages=[]
if "memory" not in st.session_state: st.session_state.memory=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None
if "image_story" not in st.session_state: st.session_state.image_story=[]
if "free_image_quota" not in st.session_state: st.session_state.free_image_quota=10
if "chat_options_visible" not in st.session_state: st.session_state.chat_options_visible=True

# -----------------------
# Quick Login / Free Flow
# -----------------------
if not st.session_state.logged_in:
    st.title("⚡ Alpha AI Login / Quick Free Access")
    name = st.text_input("Operator Name")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login / Start"):
            if name:
                st.session_state.logged_in=True
                st.session_state.user_full_name=name
                st.session_state.free_image_quota=10
                st.rerun()
            else:
                st.warning("Enter name to proceed")
    with col2:
        if st.button("🚀 Quick Free Access (10 Images)"):
            st.session_state.logged_in=True
            st.session_state.user_full_name=name if name else "FreeUser"
            st.session_state.free_image_quota=10
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
    st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)

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
def generate_image(prompt, style):
    url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    headers = {
        "Authorization": f"Bearer {st.secrets['STABILITY_API_KEY']}",
        "Accept": "image/*"
    }
    full_prompt = f"{style} style, {prompt}" if style else prompt
    files = {
        "prompt": (None, full_prompt),
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
    model="llama-3.3-70b-versatile" if mode=="Normal" else "openai/gpt-oss-120b"
    messages=[
        {"role":"system","content":"You are Alpha AI created by Hasith."},
        {"role":"system","content":memory},
        {"role":"user","content":prompt}
    ]
    res=client.chat.completions.create(model=model,messages=messages)
    return res.choices[0].message.content

# -----------------------
# Sidebar Controls (Slide-bar Chat Options)
# -----------------------
with st.sidebar:
    st.header("⚡ Alpha Control Panel")
    st.write(f"Operator: **{st.session_state.user_full_name}**")
    st.write(f"Remaining Free Images: {st.session_state.free_image_quota}")

    mode=st.radio("AI Mode", ["Normal","Pro"])
    voice_mode=st.checkbox("Voice Chat")
    internet_mode=st.checkbox("Internet Search")

    uploaded=st.file_uploader("Upload File")
    if uploaded:
        text=read_file(uploaded)
        st.session_state.memory.append(text)
        st.success("File loaded into memory")

    if st.button("Clear Memory"): st.session_state.memory=[]
    if st.button("Logout"):
        st.session_state.logged_in=False
        st.rerun()

    # --- Chat Options / Image Generation ---
    st.subheader("🖼 Chat Options")
    img_style = st.selectbox("Select Image Style", ["Realistic","Anime","Cyberpunk","Fantasy"])
    img_prompt = st.text_input("Describe image to generate")

    col1,col2 = st.columns(2)
    with col1:
        if st.button("Generate Photo"):
            if st.session_state.free_image_quota <=0:
                st.warning("Free 10 image quota used up")
            elif img_prompt.strip()=="":
                st.warning("Enter prompt first")
            else:
                with st.spinner("Generating image..."):
                    img=generate_image(img_prompt,img_style)
                    if img:
                        st.session_state.image_story.append({"prompt":img_prompt,"style":img_style,"image":img})
                        st.session_state.free_image_quota -=1
                        st.success(f"Image generated! Remaining quota: {st.session_state.free_image_quota}")
    with col2:
        if st.button("Summarize"):
            last_prompt=st.session_state.image_story[-1]["prompt"] if st.session_state.image_story else "No image yet"
            st.info(f"Last image prompt: {last_prompt}")

# -----------------------
# Main Chat Area
# -----------------------
st.title(f"Welcome {st.session_state.user_full_name}")
st.write("Alpha AI ready...")

# Display all chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------
# Chat Input
# -----------------------
user_input = st.chat_input("Ask Alpha...")

if user_input:
    # Append user message
    st.session_state.messages.append({"role":"user","content":user_input})

    # Generate AI response
    prompt_text = user_input
    if internet_mode:
        prompt_text += "\n\nInternet Data:\n" + internet_search(user_input)
    with st.spinner("Thinking..."):
        answer = ask_ai(prompt_text, mode)
    st.session_state.messages.append({"role":"assistant","content":answer})
    
    if voice_mode:
        asyncio.run(speak_alpha(answer))
    
    st.rerun()

# -----------------------
# Display Image Story (Last 10)
# -----------------------
if st.session_state.image_story:
    st.subheader("🖼 Image Story (Last 10 Images)")
    for idx, entry in enumerate(reversed(st.session_state.image_story[-10:])):
        st.markdown(f"**Prompt:** {entry['prompt']} | **Style:** {entry['style']}")
        st.image(entry["image"], use_column_width=True)
        st.download_button(
            label="Download Image",
            data=entry["image"],
            file_name=f"image_story_{len(st.session_state.image_story)-idx}.png",
            mime="image/png"
        )
        st.markdown("---")
