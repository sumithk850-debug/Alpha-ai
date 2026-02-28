import streamlit as st
from groq import Groq
import base64
import sys
from io import StringIO

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Extreme", page_icon="⚡", layout="centered")

# 2. Enhanced CSS
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
    .stChatMessage { background-color: transparent !important; border: none !important; }
    /* Stop Button Styling */
    .stButton>button { color: #ff4b4b; border-color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 3. Branding
st.markdown('<h1 class="hasith-header">Alpha AI <span style="color:#FFD700;">⚡</span></h1>', unsafe_allow_html=True)
st.write(f"**Current Status:** {'🔴 Pro Logic Active' if 'Pro' in st.sidebar.get('ai_mode', 'Normal') else '🔵 Brother Mode Active'}")
st.write("---")

# 4. Memory Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. API Setup
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# 6. Sidebar
with st.sidebar:
    st.title("⚙️ System Control")
    ai_mode = st.radio("Select Mode:", ["Normal (Big Brother)", "Pro (Deep Expert)"], key="ai_mode")
    
    st.write("---")
    st.subheader("🛠️ Tuning")
    temp_val = st.slider("Creativity:", 0.0, 1.0, 0.4 if "Pro" in ai_mode else 0.7)
    
    # 🛑 Stop Functionality
    if st.button("🛑 Force Stop Generation", use_container_width=True):
        st.warning("Generation Halted.")
        st.stop()

    st.write("---")
    uploaded_file = st.file_uploader("📸 Vision", type=["jpg", "jpeg", "png"]) if "Pro" in ai_mode else None
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 7. Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. AI Logic
if prompt := st.chat_input("Ask Alpha anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        spinner_msg = "🧠 Alpha is Analyzing Deeply..." if "Pro" in ai_mode else "👦 Big Brother is thinking..."
        
        with st.spinner(spinner_msg):
            # Dynamic System Prompting
            if "Pro" in ai_mode:
                system_prompt = (
                    "You are Alpha AI ⚡ (Pro Mode), the most advanced intelligence created by Hasith. "
                    "Your goal is ABSOLUTE PRECISION. Do not make a single factual or grammatical error. "
                    "Analyze questions with scientific depth. Provide long, comprehensive, and structural answers. "
                    "Use high-level vocabulary and remain strictly professional."
                )
            else:
                system_prompt = (
                    "You are Alpha AI ⚡, Hasith's helpful big brother. "
                    "Answer simply and kindly. Don't be too technical. Keep it friendly."
                )

            # Model Selection
            model = "llama-3.2-11b-vision-instant" if ("Pro" in ai_mode and uploaded_file) else "llama-3.3-70b-versatile"
            
            # Payload Construction
            if "Pro" in ai_mode and uploaded_file:
                payload = [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.encodebytes(uploaded_file.read()).decode()}"}}]}]
            else:
                payload = [{"role": "system", "content": system_prompt}] + st.session_state.messages

            try:
                response_container = st.empty()
                completion = client.chat.completions.create(
                    messages=payload, 
                    model=model, 
                    temperature=temp_val,
                    max_tokens=2048 if "Pro" in ai_mode else 512
                )
                full_response = completion.choices[0].message.content
                response_container.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Error: {e}")
        
