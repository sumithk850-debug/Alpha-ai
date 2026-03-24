import streamlit as st
from groq import Groq
import requests
import io
import base64
import asyncio
from PIL import Image
import edge_tts

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
HF_TOKEN = st.secrets.get("HF_TOKEN")

# -----------------------
# IMAGE GENERATION VIA HF API
# -----------------------
def generate_image(prompt):
    models = [
        "black-forest-labs/FLUX.1-schnell",
        "runwayml/stable-diffusion-v1-5"
    ]

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    for model in models:
        url = f"https://api-inference.huggingface.co/models/{model}"

        for attempt in range(5):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json={"inputs": prompt},
                    timeout=300
                )

                if response.status_code == 200:
                    content_type = response.headers.get("content-type", "")

                    if "image" in content_type:
                        return Image.open(io.BytesIO(response.content))

                    try:
                        data = response.json()
                        st.warning(f"Model response: {data}")
                    except Exception:
                        st.warning("Model returned a response, but it was not an image.")
                    break

                elif response.status_code == 503:
                    st.warning(f"{model} is busy. Retry {attempt + 1}/5")
                    import time
                    time.sleep(8)
                    continue

                else:
                    try:
                        err = response.json()
                    except Exception:
                        err = response.text
                    st.warning(f"{model} error: {err}")
                    break

            except Exception as e:
                st.warning(f"Request failed for {model}: {e}")
                import time
                time.sleep(5)

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
        with st.spinner("Generating image..."):
            img = generate_image(prompt)

            if img:
                st.image(img)

                buf = io.BytesIO()
                img.save(buf, format="PNG")

                st.download_button(
                    "Download Image",
                    buf.getvalue(),
                    file_name="alpha.png",
                    mime="image/png"
                )
            else:
                st.error("Image generation failed. Try again later.")
    else:
        st.warning("Please enter a prompt first.")

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
                    placeholder.write(full + "▌")

            placeholder.write(full)

            st.session_state.messages.append({
                "role": "assistant",
                "content": full
            })

            asyncio.run(speak(full))

        except Exception as e:
            st.error(f"Chat Error: {e}")
