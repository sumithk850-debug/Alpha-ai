import streamlit as st
from groq import Groq
import base64
import sys
from io import StringIO

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Extreme", page_icon="⚡", layout="centered")

# 2. Advanced CSS for Professional UI
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .hasith-header {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 55px;
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    /* Removed boxes for a cleaner chat look */
    .stChatMessage { background-color: transparent !important; border: none !important; }
    /* Force Stop Button Styling */
    .stButton>button { color: #ff4b4b !important; border-color: #ff4b4b !important; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Memory Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Groq Setup
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

# 5. Sidebar - Control Panel
with st.sidebar:
    st.title("⚙️ System Control")
    # AI Mode Selection
    ai_mode = st.radio(
        "Select Intelligence Mode:",
        ["Normal (Big Brother)", "Pro (Deep Expert)"],
        index=0,
        key="mode_selection"
    )
    
    st.write("---")
    st.subheader("🛠️ Tuning")
    # Temperature adjustment based on precision needs
    default_temp = 0.4 if "Pro" in ai_mode else 0.7
    temp_val = st.slider("Precision Level:", 0.0, 1.0, default_temp)
    
    # Force Stop Button
    if st.button("🛑 Force Stop Generation", use_container_width=True):
        st.warning("All processes halted.")
        st.stop()

    st.write("---")
    # Vision Upload only for Pro
    uploaded_file = st.file_uploader("📸 Vision Analysis", type=["jpg", "jpeg", "png"]) if "Pro" in ai_mode else None
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 6. Header
st.markdown('<h1 class="hasith-header">Alpha AI <span style="color:#FFD700;">⚡</span></h1>', unsafe_allow_html=True)
status_label = "🔴 Deep Precision Active" if "Pro" in ai_mode else "🔵 Simple Brother Active"
st.write(f"**System Status:** {status_label}")
st.write("---")

# 7. Image Encoding Helper
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# 8. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 9. Intelligence Logic
if prompt := st.chat_input("Ask Alpha anything..."):
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        # Dynamic Thinking Message
        spinner_msg = "🧠 Alpha is Analyzing with Deep Logic..." if "Pro" in ai_mode else "👦 Big Brother is thinking..."
        
        with st.spinner(spinner_msg):
            # Dynamic System Personas
            if "Pro" in ai_mode:
                system_prompt = (
                    "You are Alpha AI ⚡ (Pro Mode), an extreme expert intelligence. "
                    "Your mission is ABSOLUTE PRECISION. Never make a factual or logical error. "
                    "Provide highly structured, scientific, and deep responses. "
                    "Analyze every aspect of the question before answering. "
                    "Use formal language and zero slang."
                )
            else:
                system_prompt = (
                    "You are Alpha AI ⚡, Hasith's wise big brother. "
                    "Explain things simply, kindly, and briefly. "
                    "Use everyday language so anyone can understand."
                )

            # Payload Construction
            if "Pro" in ai_mode and uploaded_file:
                model_name = "llama-3.2-11b-vision-instant"
                base64_img = encode_image(uploaded_file)
                messages_payload = [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ]
                }]
            else:
                model_name = "llama-3.3-70b-versatile"
                messages_payload = [
                    {"role": "system", "content": system_prompt}
                ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

            # API Call
            try:
                chat_completion = client.chat.completions.create(
                    messages=messages_payload,
                    model=model_name,
                    temperature=temp_val,
                    max_tokens=2500 if "Pro" in ai_mode else 800
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"System Error: {e}")
