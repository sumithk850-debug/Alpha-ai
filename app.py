import streamlit as st
from groq import Groq
import base64

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Pro", page_icon="⚡", layout="centered")

# 2. Custom CSS for Premium Dark UI
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
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Branding Header Section
st.markdown('<h1 class="hasith-header">Alpha AI <span class="hasith-header-lightning">⚡</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hasith-subheader">Powered by DeepSeek-R1 & Llama 90B | Created by Hasith</p>', unsafe_allow_html=True)
st.write("---")

# 4. Initialize Session State (Memory)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Groq Client Setup
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("GROQ_API_KEY is missing in Streamlit Secrets!")
    st.stop()

# 6. Sidebar Controls
with st.sidebar:
    st.title("⚙️ Alpha Control")
    
    # Intelligence Mode Selector
    ai_mode = st.radio(
        "Intelligence Mode:",
        ["Normal (Fast Reasoning)", "Pro (Ultra Vision)"],
        index=0
    )
    
    st.write("---")
    
    # Image Uploader (Visible only in Pro Mode)
    uploaded_file = None
    if "Pro" in ai_mode:
        st.success("Vision System: Online (90B)")
        uploaded_file = st.file_uploader("📸 Upload image for analysis", type=["jpg", "jpeg", "png"])
    else:
        st.info("System: Pure Reasoning Mode")

    # Clear Button
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 7. Image Encoding Helper
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# 8. Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 9. AI Interaction Logic
if prompt := st.chat_input(f"Message Alpha ({ai_mode})..."):
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Alpha is processing..."):
            
            # CASE 1: Pro Mode with Image (Using Llama 3.2 90B Vision)
            if "Pro" in ai_mode and uploaded_file:
                # Using the large 90B model as requested
                model_name = "llama-3.2-90b-vision-preview" 
                try:
                    base64_image = encode_image(uploaded_file)
                    messages_payload = [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"User (Hasith) says: {prompt}"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }]
                except Exception as e:
                    st.error(f"Image Encoding Error: {e}")
                    st.stop()
            
            # CASE 2: Text Reasoning (Using DeepSeek-R1)
            else:
                # High-level reasoning model
                model_name = "deepseek-r1-distill-llama-70b"
                messages_payload = [
                    {"role": "system", "content": "You are Alpha AI ⚡, a super-intelligent assistant created by Hasith. Use deep reasoning and logic."}
                ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

            # Execute API Request
            try:
                chat_completion = client.chat.completions.create(
                    messages=messages_payload,
                    model=model_name,
                    temperature=0.6
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                # Error Handling for 404 (Model Unavailable)
                st.error(f"Error: {e}")
                if "404" in str(e) or "model_not_found" in str(e):
                    st.warning("Note: llama-3.2-90b-vision might be unavailable on your Groq tier. Try switching to Normal or check Groq docs.")
   
