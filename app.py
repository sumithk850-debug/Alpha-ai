import streamlit as st
import requests
from huggingface_hub import InferenceClient
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import io

# -----------------------
# CONFIG
# -----------------------

HF_TOKEN = "PUT_YOUR_HF_TOKEN_HERE"

image_client = InferenceClient(
    model="stabilityai/stable-diffusion-2",
    token=HF_TOKEN
)

# -----------------------
# SESSION STATE
# -----------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "memory" not in st.session_state:
    st.session_state.memory = []

if "image_story" not in st.session_state:
    st.session_state.image_story = []

if "free_image_quota" not in st.session_state:
    st.session_state.free_image_quota = 10

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_full_name" not in st.session_state:
    st.session_state.user_full_name = ""

# -----------------------
# LOGIN
# -----------------------

if not st.session_state.logged_in:

    st.title("⚡ Alpha AI Login")

    name = st.text_input("Enter your name")

    if st.button("Start Alpha AI"):

        if name:

            st.session_state.logged_in = True
            st.session_state.user_full_name = name
            st.rerun()

        else:

            st.warning("Enter your name")

    st.stop()

# -----------------------
# FILE READER
# -----------------------

def read_file(upload):

    if upload.name.endswith(".pdf"):

        reader = PdfReader(upload)

        text = ""

        for page in reader.pages:
            text += page.extract_text()

        return text[:3000]

    else:

        return upload.read().decode()

# -----------------------
# INTERNET SEARCH
# -----------------------

def internet_search(query):

    url = f"https://www.google.com/search?q={query}"

    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    results = [g.text for g in soup.select("div.BNeawe")[:5]]

    return "\n".join(results)

# -----------------------
# IMAGE GENERATION
# -----------------------

def generate_image(prompt, style):

    full_prompt = f"{prompt}, {style} style"

    image = image_client.text_to_image(full_prompt)

    return image

# -----------------------
# SIDEBAR
# -----------------------

with st.sidebar:

    st.header("⚡ Alpha Control Panel")

    st.write(f"User: **{st.session_state.user_full_name}**")

    st.write(f"Free Images Left: {st.session_state.free_image_quota}")

    internet_mode = st.checkbox("Internet Search")

    uploaded = st.file_uploader("Upload File")

    if uploaded:

        text = read_file(uploaded)

        st.session_state.memory.append(text)

        st.success("File added to memory")

    if st.button("Clear Memory"):

        st.session_state.memory = []

# -----------------------
# IMAGE GENERATION PANEL
# -----------------------

    st.subheader("🖼 Image Generator")

    img_prompt = st.text_input("Describe image")

    style = st.selectbox(

        "Style",

        ["Realistic", "Anime", "Cyberpunk", "Fantasy", "Digital Art"]

    )

    if st.button("Generate Image"):

        if st.session_state.free_image_quota <= 0:

            st.warning("Image quota finished")

        elif img_prompt == "":

            st.warning("Enter prompt")

        else:

            with st.spinner("Generating..."):

                img = generate_image(img_prompt, style)

                st.session_state.image_story.append(

                    {"prompt": img_prompt, "style": style, "image": img}

                )

                st.session_state.free_image_quota -= 1

                st.success("Image generated!")

# -----------------------
# MAIN CHAT
# -----------------------

st.title("⚡ Alpha AI Assistant")

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])

user_input = st.chat_input("Ask Alpha AI...")

if user_input:

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    answer = user_input

    if internet_mode:

        answer += "\n\nInternet Data:\n" + internet_search(user_input)

    response = f"Alpha AI Response:\n{answer}"

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    st.rerun()

# -----------------------
# IMAGE STORY
# -----------------------

if st.session_state.image_story:

    st.subheader("🖼 Image Story")

    for entry in reversed(st.session_state.image_story[-10:]):

        st.markdown(
            f"**Prompt:** {entry['prompt']} | **Style:** {entry['style']}"
        )

        st.image(entry["image"])

        buf = io.BytesIO()

        entry["image"].save(buf, format="PNG")

        st.download_button(

            "Download",

            buf.getvalue(),

            file_name="alpha_ai_image.png",

            mime="image/png"

        )

        st.markdown("---")
