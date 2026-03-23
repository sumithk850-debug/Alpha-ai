import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
import requests, base64, asyncio, io
import edge_tts
from PIL import Image

# -----------------------
# 1. Page Config
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")

# -----------------------
# 2. Session State
# -----------------------
if "messages" not in st.session_state: st.session_state.messages=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None

# -----------------------
# 3. UI Styling
# -----------------------
st.markdown("""
<style>
.premium-banner {
    width:100%; padding:15px;
    background: linear-gradient(90deg, #FFD700, #FF8C00);
    color:#000; border-radius:15px;
    text-align:center; font-weight:bold;
    margin-bottom:20px; font-size: 22px;
}
.lab-box {
    border: 1px solid #333;
    padding: 20px;
    border-radius: 15px;
    background: #0e1117;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# 4. Login (SECURE)
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    name = st.text_input("Operator Name")
    password = st.text_input("Master Key", type="password")

    if st.button("Initialize Alpha"):
        if password == st.secrets.get("APP_PASSWORD"):
            st.session_state.user_full_name = name or "Operator"
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Access Denied")

    st.stop()

# -----------------------
# 5. API Setup
# -----------------------
groq_client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
hf_client = InferenceClient(token=st.secrets.get("HF_TOKEN"))

# -----------------------
# 6. Voice Function
# -----------------------
async def speak(text):
    try:
        comm = edge_tts.Communicate(text, "en-US-SteffanNeural")
        audio = b""
        async for chunk in comm.stream():
            if chunk["type"]=="audio":
                audio += chunk["data"]

        if audio:
            b64 = base64.b64encode(audio).decode()
            st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except:
        pass

# -----------------------
# 7. Cached Image Generation
# -----------------------
@st.cache_data(show_spinner=False)
def generate_image(prompt):
    try:
        return hf_client.text_to_image(prompt, model="runwayml/stable-diffusion-v1-5")
    except:
        # fallback model
        return hf_client.text_to_image(prompt, model="stabilityai/stable-diffusion-2-1")

# -----------------------
# 8. Sidebar
# -----------------------
with st.sidebar:
    st.title("Alpha Control")
    st.write(f"Operator: {st.session_state.user_full_name}")

    mode = st.radio("Mode", ["Fast", "Smart"])
    voice_on = st.checkbox("Voice", value=True)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# -----------------------
# 9. Header
# -----------------------
st.markdown('<div class="premium-banner">⚡ ALPHA AI ULTIMATE</div>', unsafe_allow_html=True)

# -----------------------
# 10. Image Generation
# -----------------------
st.subheader("🖼 Image Generation")

img_prompt = st.text_input("Describe image")

if st.button("Generate Image"):
    if img_prompt:
        with st.spinner("Generating..."):
            try:
                img = generate_image(img_prompt)
                if img:
                    st.image(img)

                    buf = io.BytesIO()
                    img.save(buf, format="PNG")

                    st.download_button(
                        "Download",
                        buf.getvalue(),
                        "alpha.png"
                    )
            except Exception as e:
                st.error(f"Error: {e}")

# -----------------------
# 11. Chat System
# -----------------------
st.subheader("💬 Chat")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask Alpha...")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()

        model = "llama-3.3-70b-versatile" if mode=="Fast" else "openai/gpt-oss-120b"

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

            st.session_state.messages.append({"role":"assistant","content":full_res})

        except Exception as e:
            st.error(f"Error: {e}")
