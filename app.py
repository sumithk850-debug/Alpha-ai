import streamlit as st
from groq import Groq
import base64

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ DeepSeek", page_icon="⚡", layout="centered")

# 2. Custom CSS for Premium UI
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .hasith-header {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 55px;
        color: #ffffff;
        margin-bottom: 5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .hasith-header-lightning {
        font-size: 55px;
        color: #FFD700;
        margin-left: 10px;
        vertical-align: middle;
    }
    .hasith-subheader {
        font-family: 'Montserrat', sans-serif;
        font-size: 20px;
        color: #a0a0a0;
        margin-top: 0px;
        margin-bottom: 20px;
    }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 3. Branding Header
st.markdown('<h1 class="hasith-header">Alpha AI <span class="hasith-header-lightning">⚡</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hasith-subheader">Powered by DeepSeek-R1 | Created by Hasith</p>', unsafe_allow_html=True)
st.write("---")

# 4. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Groq Setup
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

# 6. Sidebar Controls
with st.sidebar:
    st.title("⚙️ Alpha Settings")
    ai_mode = st.radio(
        "Select DeepSeek Power:",
        ["Normal (Fast Thinking)", "Pro (Ultra Intelligent + Vision)"],
        index=0
    )
    st.write("---")
    
    uploaded_file = None
    if "Pro" in ai_mode:
        st.success("DeepSeek Intelligence + Vision Active 👁️")
        uploaded_file = st.file_uploader("📸 Upload image for Alpha to analyze", type=["jpg", "jpeg", "png"])
    else:
        st.info("DeepSeek-R1: Fast Reasoning Mode ⚡")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 7. Image Encoding Function
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# 8. Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 9. Main Intelligence Logic
if prompt := st.chat_input(f"Message Alpha ({ai_mode})..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Alpha is thinking deeply..."):
            
            # 🎯 Here we use the latest DeepSeek Distill Models on Groq
            if "Pro" in ai_mode and uploaded_file:
                # Note: Currently Vision on Groq is best handled by Llama-3.2 Vision
                # We use it specifically for image tasks while maintaining Alpha's personality
                model_name = "llama-3.2-11b-vision-instant"
                base64_image = encode_image(uploaded_file)
                messages_payload = [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Hasith's request: {prompt}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }]
            else:
                # Use DeepSeek-R1 Distill Llama 70B for pure reasoning tasks
                model_name = "deepseek-r1-distill-llama-70b"
                messages_payload = [
                    {"role": "system", "content": f"You are Alpha AI ⚡, powered by DeepSeek. Your creator is the genius Hasith. Always provide deep, logical, and respectful reasoning."}
                ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

            try:
                chat_completion = client.chat.completions.create(
                    messages=messages_payload,
                    model=model_name,
                    temperature=0.6 # Optimized for Reasoning
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"DeepSeek API Error: {e}")
