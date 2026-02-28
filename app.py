import streamlit as st
from groq import Groq
import base64

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Pro", page_icon="⚡", layout="centered")

# 2. Custom CSS for UI (Removed the box border from chat)
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
        font-size: 18px;
        color: #a0a0a0;
        margin-top: 0px;
        margin-bottom: 20px;
    }
    /* Removed box styling to make it look natural */
    .stChatMessage { 
        background-color: transparent !important; 
        border: none !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Branding Header
st.markdown('<h1 class="hasith-header">Alpha AI <span class="hasith-header-lightning">⚡</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hasith-subheader">Powered by Llama 3.3 70B | Created by Hasith</p>', unsafe_allow_html=True)
st.write("---")

# 4. Initialize Memory
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
        "Select Mode:",
        ["Normal (70B)", "Pro (Vision)"],
        index=0
    )
    st.write("---")
    
    uploaded_file = None
    if ai_mode == "Pro (Vision)":
        st.success("Vision Mode: Active 👁️")
        uploaded_file = st.file_uploader("📸 Upload image", type=["jpg", "jpeg", "png"])
    else:
        st.info("Chat Mode: Active ⚡")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 7. Image Encoding Function
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# 8. Display Chat History (Clean Style)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 9. Main AI Logic
if prompt := st.chat_input(f"Message Alpha ({ai_mode})..."):
    # Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant Response with "Thinking" Spinner
    with st.chat_message("assistant"):
        # 🎯 This is the spinner Hasith requested
        with st.spinner("Alpha is thinking..."):
            
            # Logic to select model
            if ai_mode == "Pro (Vision)" and uploaded_file:
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
                model_name = "llama-3.3-70b-versatile"
                messages_payload = [
                    {"role": "system", "content": "You are Alpha AI, a super-intelligent assistant created by Hasith."}
                ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

            try:
                chat_completion = client.chat.completions.create(
                    messages=messages_payload,
                    model=model_name,
                    temperature=0.7
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {e}")
