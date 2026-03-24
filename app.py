import streamlit as st
from groq import Groq
import requests, io, time, base64, asyncio
from PIL import Image
import edge_tts
import torch
from diffusers import StableDiffusionPipeline

# -----------------------
# CONFIG
# -----------------------
st.set_page_config(page_title="Alpha AI Ultimate", layout="wide")

# -----------------------
# SESSION
# -----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -----------------------
# LOGIN
# -----------------------
if not st.session_state.logged_in:
    st.title("Alpha AI Login")

    password = st.text_input("Master Key", type="password")

    if st.button("Login"):
        if password == st.secrets.get("APP_PASSWORD"):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong Password")

    st.stop()

# -----------------------
# API KEYS
# -----------------------
groq_client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

# -----------------------
# LOAD MODEL (CPU SAFE)
# -----------------------
@st.cache_resource
def load_pipe():
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True
    )
    pipe = pipe.to("cpu")
    return pipe

pipe = load_pipe()

# -----------------------
# IMAGE GENERATION
# -----------------------
def generate_image(prompt):
    try:
        image = pipe(
            prompt,
            num_inference_steps=15,
            guidance_scale=7.0,
            height=384,
            width=384
        ).images[0]

        return image

    except Exception as e:
        st.error(f"Image Error: {e}")
        return None

# -----------------------
# VOICE
# -----------------------
async def speak(text):
    try:
        comm = edge_tts.Communicate(text, "en-US-SteffanNeural")
        audio = b""

        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                audio += chunk["data"]

        if audio:
            b64 = base64.b64encode(audio).decode()
            st.markdown(
                f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>',
                unsafe_allow_html=True
            )
    except:
        pass

# -----------------------
# UI
# -----------------------
st.title("Alpha AI Ultimate")

# IMAGE SECTION
st.subheader("Generate Image")

prompt = st.text_input("Enter prompt")

if st.button("Generate Image"):
    if prompt:
        with st.spinner("Generating..."):
            img = generate_image(prompt)

            if img:
                st.image(img)

                buf = io.BytesIO()
                img.save(buf, format="PNG")

                st.download_button(
                    "Download Image",
                    buf.getvalue(),
                    "alpha.png"
                )
            else:
                st.error("Failed to generate image")

# -----------------------
# CHAT SECTION
# -----------------------
st.subheader("Chat")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("assistant"):
        placeholder = st.empty()

        try:
            stream = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages[-10:],
                temperature=0.5,
                stream=True
            )

            full = ""

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full += chunk.choices[0].delta.content
                    placeholder.write(full + "...")

            placeholder.write(full)

            st.session_state.messages.append({
                "role": "assistant",
                "content": full
            })

            asyncio.run(speak(full))

        except Exception as e:
            st.error(f"Chat Error: {e}")
