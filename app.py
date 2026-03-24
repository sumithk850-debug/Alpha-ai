import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
import base64, asyncio, io
import edge_tts

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(page_title="Alpha AI", layout="wide", page_icon="⚡")

# -----------------------
# SESSION STATE
# -----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_full_name" not in st.session_state:
    st.session_state.user_full_name = ""

# -----------------------
# LOGIN SYSTEM
# -----------------------
if not st.session_state.logged_in:
    st.title("🔐 Alpha AI Login")

    name = st.text_input("Operator Name")
    password = st.text_input("Master Key", type="password")

    if st.button("Login"):
        if password == st.secrets.get("APP_PASSWORD"):
            st.session_state.logged_in = True
            st.session_state.user_full_name = name if name else "Operator"
            st.rerun()
        else:
            st.error("❌ Wrong Master Key")

    st.stop()

# -----------------------
# API SETUP
# -----------------------
groq_client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
hf_client = InferenceClient(token=st.secrets.get("HF_TOKEN"))

# -----------------------
# VOICE FUNCTION
# -----------------------
async def speak(text):
    try:
        communicate = edge_tts.Communicate(text, "en-US-SteffanNeural")
        audio_bytes = b""

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]

        if audio_bytes:
            b64 = base64.b64encode(audio_bytes).decode()
            st.markdown(
                f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>',
                unsafe_allow_html=True
            )
    except:
        pass

# -----------------------
# IMAGE GENERATION (FIXED)
# -----------------------
@st.cache_data(show_spinner=False)
def generate_image(prompt):
    try:
        image = hf_client.text_to_image(
            prompt,
            model="runwayml/stable-diffusion-v1-5"
        )
        return image
    except:
        return None

# -----------------------
# SIDEBAR
# -----------------------
with st.sidebar:
    st.title("⚡ Alpha Control")
    st.write(f"Operator: {st.session_state.user_full_name}")

    mode = st.radio("Mode", ["Fast", "Smart"])
    voice_on = st.checkbox("Voice Output", value=True)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# -----------------------
# MAIN HEADER
# -----------------------
st.title("⚡ Alpha AI Ultimate")

# -----------------------
# IMAGE SECTION
# -----------------------
st.subheader("🖼 Generate Image")

img_prompt = st.text_input("Enter image prompt")

if st.button("Generate Image"):
    if img_prompt:
        with st.spinner("Generating image..."):
            img = generate_image(img_prompt)

            if img is not None:
                st.image(img)

                buf = io.BytesIO()
                img.save(buf, format="PNG")

                st.download_button(
                    "Download Image",
                    buf.getvalue(),
                    "alpha.png"
                )
            else:
                st.error("❌ Image generation failed")

# -----------------------
# CHAT SECTION
# -----------------------
st.subheader("💬 Chat")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask Alpha...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()

        if mode == "Fast":
            model = "llama-3.3-70b-versatile"
        else:
            model = "openai/gpt-oss-120b"

        try:
            stream = groq_client.chat.completions.create(
                model=model,
                messages=st.session_state.messages[-10:],
                temperature=0.5,
                stream=True
            )

            full_response = ""

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)

            if voice_on:
                asyncio.run(speak(full_response))

            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:
            st.error(f"Chat Error: {e}")
