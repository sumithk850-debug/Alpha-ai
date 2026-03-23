import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
import base64, asyncio, io
import edge_tts

# -----------------------
# 1. Page Config
# -----------------------
st.set_page_config(page_title="Alpha AI", layout="wide", page_icon="⚡")

# -----------------------
# 2. Session State
# -----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_full_name" not in st.session_state:
    st.session_state.user_full_name = None

# -----------------------
# 3. Login System (SECURE)
# -----------------------
if not st.session_state.logged_in:
    st.title("🔐 Alpha AI Login")

    name = st.text_input("Operator Name")
    password = st.text_input("Master Key", type="password")

    if st.button("Login"):
        if password == st.secrets.get("APP_PASSWORD"):
            st.session_state.logged_in = True
            st.session_state.user_full_name = name or "Operator"
            st.rerun()
        else:
            st.error("Wrong Master Key")

    st.stop()

# -----------------------
# 4. API Setup
# -----------------------
groq_client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
hf_client = InferenceClient(token=st.secrets.get("HF_TOKEN"))

# -----------------------
# 5. Voice
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
            st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except:
        pass

# -----------------------
# 6. Image Generator (FIXED)
# -----------------------
@st.cache_data(show_spinner=False)
def generate_image(prompt):
    try:
        return hf_client.text_to_image(
            prompt,
            model="runwayml/stable-diffusion-v1-5"
        )
    except Exception as e:
        return None

# -----------------------
# 7. Sidebar
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
# 8. Header
# -----------------------
st.title("⚡ Alpha AI Ultimate")

# -----------------------
# 9. Image Generation
# -----------------------
st.subheader("🖼 Generate Image")

prompt = st.text_input("Enter your prompt")

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
                st.error("Image generation failed 😢")

# -----------------------
# 10. Chat System
# -----------------------
st.subheader("💬 Chat")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()

        model = "llama-3.3-70b-versatile" if mode == "Fast" else "openai/gpt-oss-120b"

        try:
            stream = groq_client.chat.completions.create(
                model=model,
                messages=st.session_state.messages[-10:],
                temperature=0.5,
                stream=True
            )

            full_res = ""

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    placeholder.markdown(full_res + "▌")

            placeholder.markdown(full_res)

            if voice_on:
                asyncio.run(speak(full_res))

            st.session_state.messages.append({"role": "assistant", "content": full_res})

        except Exception as e:
            st.error(f"Chat Error: {e}")import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
import base64, asyncio, io
import edge_tts

# -----------------------
# 1. Page Config
# -----------------------
st.set_page_config(page_title="Alpha AI", layout="wide", page_icon="⚡")

# -----------------------
# 2. Session State
# -----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_full_name" not in st.session_state:
    st.session_state.user_full_name = None

# -----------------------
# 3. Login System (SECURE)
# -----------------------
if not st.session_state.logged_in:
    st.title("🔐 Alpha AI Login")

    name = st.text_input("Operator Name")
    password = st.text_input("Master Key", type="password")

    if st.button("Login"):
        if password == st.secrets.get("APP_PASSWORD"):
            st.session_state.logged_in = True
            st.session_state.user_full_name = name or "Operator"
            st.rerun()
        else:
            st.error("Wrong Master Key")

    st.stop()

# -----------------------
# 4. API Setup
# -----------------------
groq_client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
hf_client = InferenceClient(token=st.secrets.get("HF_TOKEN"))

# -----------------------
# 5. Voice
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
            st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except:
        pass

# -----------------------
# 6. Image Generator (FIXED)
# -----------------------
@st.cache_data(show_spinner=False)
def generate_image(prompt):
    try:
        return hf_client.text_to_image(
            prompt,
            model="runwayml/stable-diffusion-v1-5"
        )
    except Exception as e:
        return None

# -----------------------
# 7. Sidebar
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
# 8. Header
# -----------------------
st.title("⚡ Alpha AI Ultimate")

# -----------------------
# 9. Image Generation
# -----------------------
st.subheader("🖼 Generate Image")

prompt = st.text_input("Enter your prompt")

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
                st.error("Image generation failed 😢")

# -----------------------
# 10. Chat System
# -----------------------
st.subheader("💬 Chat")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()

        model = "llama-3.3-70b-versatile" if mode == "Fast" else "openai/gpt-oss-120b"

        try:
            stream = groq_client.chat.completions.create(
                model=model,
                messages=st.session_state.messages[-10:],
                temperature=0.5,
                stream=True
            )

            full_res = ""

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    placeholder.markdown(full_res + "▌")

            placeholder.markdown(full_res)

            if voice_on:
                asyncio.run(speak(full_res))

            st.session_state.messages.append({"role": "assistant", "content": full_res})

        except Exception as e:
            st.error(f"Chat Error: {e}")
