import streamlit as st
from huggingface_hub import InferenceClient
from PIL import Image
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io

# HuggingFace Token
HF_TOKEN = "YOUR_HF_TOKEN"

# Image model
image_client = InferenceClient(
    model="stabilityai/stable-diffusion-xl-base-1.0",
    token=HF_TOKEN
)

# Page setup
st.set_page_config(page_title="Alpha AI", page_icon="⚡")

# Session state
if "images_left" not in st.session_state:
    st.session_state.images_left = 10

# Header
st.title("⚡ Alpha Control Panel")
st.write("User: Hasith")
st.write(f"Free Images Left: {st.session_state.images_left}")

# -------------------------
# FILE UPLOAD
# -------------------------

st.subheader("Upload File")

uploaded_file = st.file_uploader(
    "Drag and drop file here",
    type=["txt", "pdf"]
)

if uploaded_file:

    if uploaded_file.type == "application/pdf":

        pdf_reader = PyPDF2.PdfReader(uploaded_file)

        text = ""

        for page in pdf_reader.pages:
            text += page.extract_text()

        st.text_area("PDF Content", text, height=200)

    else:

        text = uploaded_file.read().decode()
        st.text_area("File Content", text, height=200)

# -------------------------
# WEBSITE SCRAPER
# -------------------------

st.subheader("Website Reader")

url = st.text_input("Enter website URL")

if st.button("Read Website"):

    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        text = soup.get_text()

        st.text_area("Website Text", text[:2000], height=200)

    except:
        st.error("Could not read website")

# -------------------------
# IMAGE GENERATOR
# -------------------------

st.subheader("🖼 Image Generator")

prompt = st.text_input("Describe image")

style = st.selectbox(
    "Style",
    [
        "Realistic",
        "Anime",
        "Cyberpunk",
        "Fantasy",
        "Digital Art",
        "3D Render"
    ]
)

def generate_image(prompt, style):

    full_prompt = f"{prompt}, {style}, ultra detailed, cinematic lighting, 8k"

    image = image_client.text_to_image(full_prompt)

    return image


if st.button("Generate Image"):

    if st.session_state.images_left <= 0:
        st.error("No free images left")
    else:

        with st.spinner("Generating image..."):

            img = generate_image(prompt, style)

            st.image(img)

            st.session_state.images_left -= 1

            buf = io.BytesIO()
            img.save(buf, format="PNG")

            st.download_button(
                "Download Image",
                buf.getvalue(),
                "alpha_ai_image.png",
                "image/png"
            )
