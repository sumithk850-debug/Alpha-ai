import streamlit as st
import base64, asyncio
from huggingface_hub import InferenceClient
from PyPDF2 import PdfReader

# -----------------------
# 1. Page Setup
# -----------------------
st.set_page_config(page_title="Alpha AI | Jarvis v4", page_icon="⚡", layout="wide")

# -----------------------
# 2. Session State
# -----------------------
if "messages" not in st.session_state: st.session_state.messages = []
if "memory" not in st.session_state: st.session_state.memory = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_full_name" not in st.session_state: st.session_state.user_full_name = None
if "show_options" not in st.session_state: st.session_state.show_options = True

# -----------------------
# 3. Login
# -----------------------
if not st.session_state.logged_in:
    st.title("ALPHA CORE LOGIN")
    name = st.text_input("Name")
    email = st.text_input("Email")
    key = st.text_input("Master Key", type="password")
    if st.button("Login"):
        if key == "Hasith12378":
            st.session_state.logged_in = True
            st.session_state.user_full_name = name if name else "Hasith"
            st.experimental_rerun()
        else:
            st.error("Access Denied")
    st.stop()

# -----------------------
# 4. Sidebar
# -----------------------
st.sidebar.markdown(f"**User:** {st.session_state.user_full_name}")
mode = st.sidebar.radio("Intelligence Mode", ["Llama 3.3 (Normal)", "GPT OSS 120B (Pro)"])
voice_mode = st.sidebar.checkbox("🎤 Voice Chat")
memory_mode = st.sidebar.checkbox("🧠 Memory")
image_mode = st.sidebar.checkbox("🖼 Image Generation")

# -----------------------
# 5. Hugging Face Token + Client
# -----------------------
HF_TOKEN = "YOUR_NEW_HF_TOKEN_HERE"
image_client = InferenceClient(token=HF_TOKEN, model="stabilityai/stable-diffusion-xl-base-1.0")

# -----------------------
# 6. File Upload
# -----------------------
uploaded = st.file_uploader("Upload File")
if uploaded:
    if uploaded.name.endswith(".pdf"):
        reader = PdfReader(uploaded)
        text = "".join([p.extract_text() for p in reader.pages])
    else:
        text = uploaded.read().decode()
    st.session_state.memory.append(text)
    st.success("File added to memory")

# -----------------------
# 7. Chat Box
# -----------------------
st.header("💬 Chat / Commands")
user_input = st.chat_input("Type your command...")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    
    # hide options after sending
    st.session_state.show_options = False
    
    # Display user input
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # AI response
    with st.chat_message("assistant"):
        prompt = user_input
        # Here you can integrate LLaMA/GPT call, example:
        if mode.startswith("Llama"):
            answer = f"Llama response to: {prompt}"  # replace with actual API
        else:
            answer = f"GPT OSS response to: {prompt}"  # replace with actual API
        st.markdown(answer)
        st.session_state.messages.append({"role":"assistant","content":answer})

# Show past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------
# 8. Image Generation Section
# -----------------------
if image_mode and st.session_state.show_options:
    st.subheader("🖼 Image Generator")
    img_prompt = st.text_input("Describe image")
    style = st.selectbox("Style", ["Realistic", "Cyberpunk", "Futuristic", "Anime"])
    if st.button("Generate Image"):
        try:
            full_prompt = f"{img_prompt}, style: {style}"
            output = image_client.text_to_image(full_prompt)
            st.image(output)
            # Download button
            b64 = base64.b64encode(output).decode()
            href = f'<a href="data:file/png;base64,{b64}" download="generated.png">Download Image</a>'
            st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error generating image: {str(e)}")

# -----------------------
# 9. Sidebar Options Reset
# -----------------------
if st.sidebar.button("Reset Options"):
    st.session_state.show_options = True
