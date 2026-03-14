import streamlit as st
import requests
import base64
from io import BytesIO
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup

# -----------------------
# Session State
# -----------------------
if "messages" not in st.session_state: st.session_state.messages=[]
if "memory" not in st.session_state: st.session_state.memory=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None
if "image_story" not in st.session_state: st.session_state.image_story=[]
if "free_image_quota" not in st.session_state: st.session_state.free_image_quota=10

# -----------------------
# Quick Login / Free Access
# -----------------------
if not st.session_state.logged_in:
    st.title("⚡ Alpha AI Login / Free Access")
    name = st.text_input("Operator Name")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login / Start"):
            if name:
                st.session_state.logged_in=True
                st.session_state.user_full_name=name
                st.session_state.free_image_quota=10
                st.rerun()
            else: st.warning("Enter name")
    with col2:
        if st.button("🚀 Quick Free Access"):
            st.session_state.logged_in=True
            st.session_state.user_full_name=name if name else "FreeUser"
            st.session_state.free_image_quota=10
            st.rerun()
    st.stop()

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
# Internet Search (Optional)
# -----------------------
def internet_search(query):
    url=f"https://www.google.com/search?q={query}"
    headers={"User-Agent":"Mozilla/5.0"}
    r=requests.get(url, headers=headers)
    soup=BeautifulSoup(r.text,"html.parser")
    results=[g.text for g in soup.select("div.BNeawe")[:5]]
    return "\n".join(results)

# -----------------------
# Craiyon Image Generation
# -----------------------
def generate_image_craiyon(prompt):
    try:
        url = "https://backend.craiyon.com/generate"
        payload = {"prompt": prompt}
        r = requests.post(url, json=payload)
        if r.status_code==200:
            images_base64 = r.json()["images"]
            images_bytes=[]
            for img_b64 in images_base64:
                img_data = base64.b64decode(img_b64)
                images_bytes.append(img_data)
            return images_bytes
        else:
            st.error(f"Craiyon API Error: {r.status_code}")
            return []
    except:
        st.error("Craiyon API not reachable")
        return []

# -----------------------
# Sidebar Controls
# -----------------------
with st.sidebar:
    st.header("⚡ Alpha AI Control Panel")
    st.write(f"Operator: **{st.session_state.user_full_name}**")
    st.write(f"Remaining Free Images: {st.session_state.free_image_quota}")

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

    # --- Image Generation Sidebar ---
    st.subheader("🖼 Chat Options")
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
                    images=generate_image_craiyon(img_prompt)
                    if images:
                        for img_data in images[:min(10, st.session_state.free_image_quota)]:
                            st.session_state.image_story.append({"prompt":img_prompt,"image":img_data})
                            st.session_state.free_image_quota -= 1
                        st.success(f"Images generated! Remaining quota: {st.session_state.free_image_quota}")
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
    st.session_state.messages.append({"role":"user","content":user_input})

    prompt_text = user_input
    if internet_mode:
        prompt_text += "\n\nInternet Data:\n" + internet_search(user_input)
    answer = f"Alpha AI Response: {prompt_text}"  # replace with real AI model

    st.session_state.messages.append({"role":"assistant","content":answer})
    st.rerun()

# -----------------------
# Display Image Story
# -----------------------
if st.session_state.image_story:
    st.subheader("🖼 Image Story (Last 10 Images)")
    for idx, entry in enumerate(reversed(st.session_state.image_story[-10:])):
        st.markdown(f"**Prompt:** {entry['prompt']}")
        st.image(entry["image"], use_column_width=True)
        st.download_button(
            label="Download Image",
            data=entry["image"],
            file_name=f"image_story_{len(st.session_state.image_story)-idx}.png",
            mime="image/png"
        )
        st.markdown("---")
