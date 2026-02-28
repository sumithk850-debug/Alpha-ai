import streamlit as st
from groq import Groq
import base64
import sys
from io import StringIO

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Extreme", page_icon="⚡", layout="centered")

# 2. Custom CSS for Quick Buttons & UI
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
    
    /* Quick Action Buttons Styling */
    div.stButton > button:first-child {
        background-color: #1e1e1e;
        color: #FFD700;
        border: 1px solid #30363d;
        border-radius: 20px;
        font-size: 12px;
        padding: 5px 15px;
    }
    div.stButton > button:hover {
        border-color: #FFD700;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Groq Setup
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# 5. Sidebar (Tuning & Settings)
with st.sidebar:
    st.title("⚙️ System Control")
    ai_mode = st.radio("Intelligence Mode:", ["Normal (Big Brother)", "Pro (Deep Expert)"], index=0)
    st.write("---")
    st.subheader("🛠️ Professional Tuning")
    temp_val = st.slider("Creativity:", 0.0, 1.0, 0.4 if "Pro" in ai_mode else 0.7)
    max_toks = st.number_input("Max Output Length:", 128, 4096, 2500 if "Pro" in ai_mode else 800)
    context_window = st.slider("Memory Depth:", 1, 20, 10)
    st.write("---")
    uploaded_file = st.file_uploader("📸 Vision", type=["jpg", "jpeg", "png"]) if "Pro" in ai_mode else None
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 6. Main UI Header
st.markdown('<h1 class="hasith-header">Alpha AI <span style="color:#FFD700;">⚡</span></h1>', unsafe_allow_html=True)
st.info(f"System Status: {'🔴 Pro Engine Active' if 'Pro' in ai_mode else '🔵 Brother Mode Active'}")
st.write("---")

# 7. Display Chat History
for message in st.session_state.messages[-context_window:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. Quick Action Buttons Logic
st.write("Quick Actions:")
col1, col2, col3, col4 = st.columns(4)
quick_prompt = None

with col1:
    if st.button("📝 Summarize"):
        quick_prompt = "Please summarize our entire conversation so far briefly."
with col2:
    if st.button("💡 Explain More"):
        quick_prompt = "Can you explain your last point in more detail and more simply?"
with col3:
    if st.button("✅ Fix Grammar"):
        quick_prompt = "Check my previous message for any grammar or spelling mistakes and show me the corrected version."
with col4:
    if st.button("📋 Copy Chat"):
        chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        st.code(chat_text, language="text")
        st.success("Chat copied below!")

# 9. Main AI Interaction Logic
# We check if a quick prompt was clicked or a new one was typed
prompt = st.chat_input("Message Alpha...")
final_prompt = quick_prompt if quick_prompt else prompt

if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    with st.chat_message("assistant"):
        spinner_msg = "🧠 Alpha's Ultra Thinking..." if "Pro" in ai_mode else "👦 Thinking..."
        with st.spinner(spinner_msg):
            # Persona selection
            if "Pro" in ai_mode:
                system_prompt = "You are Alpha AI ⚡ (Pro Mode). Provide ABSOLUTE PRECISION and deep scientific analysis."
            else:
                system_prompt = "You are Alpha AI ⚡, a kind big brother. Keep it simple."

            # Setup Model & Payload
            model = "llama-3.2-11b-vision-instant" if ("Pro" in ai_mode and uploaded_file) else "llama-3.3-70b-versatile"
            
            if "Pro" in ai_mode and uploaded_file:
                # Vision Payload
                img_data = base64.b64encode(uploaded_file.read()).decode()
                payload = [{"role": "user", "content": [{"type": "text", "text": final_prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}}]}]
            else:
                # Text Payload
                payload = [{"role": "system", "content": system_prompt}] + st.session_state.messages[-context_window:]

            try:
                completion = client.chat.completions.create(
                    messages=payload, model=model, temperature=temp_val, max_tokens=max_toks
                )
                response = completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {e}")
