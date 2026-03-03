import streamlit as st
from groq import Groq
import sys
import time
from io import StringIO
from streamlit_mic_recorder import speech_to_text
import hashlib

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI | DeepSeek-R1", page_icon="🧠", layout="wide")

# 2. Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 3. Custom CSS Styling
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .premium-banner { 
        width: 100%; padding: 15px; 
        background: linear-gradient(90deg, #FFD700, #FFA500); 
        color: black; border-radius: 15px; 
        text-align: center; font-weight: bold; margin-bottom: 25px; 
    }
    .thinking-box { 
        padding: 15px; background-color: #1e2130; 
        border-left: 5px solid #FFD700; color: #FFD700; 
        font-family: 'Courier New', monospace; border-radius: 8px;
        margin-bottom: 15px;
    }
    div.stButton > button {
        background-color: #FFD700; color: black;
        border-radius: 10px; font-weight: bold; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# 4. Authentication (Simplified)
if not st.session_state.logged_in:
    st.title("🔐 Alpha AI Secure Login")
    user = st.text_input("Username")
    pas = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "hasith123": # Change as needed
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Access Denied")
    st.stop()

# 5. API Setup
# Ensure GROQ_API_KEY is added to your Streamlit Secrets
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API Key missing! Add 'GROQ_API_KEY' to Streamlit Secrets.")
    st.stop()

# 6. Sidebar UI
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.info("Model: DeepSeek-R1-70B")
    temp = st.slider("Creativity (Temperature):", 0.0, 1.5, 0.7)
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# 7. Main Chat UI
st.markdown('<div class="premium-banner">⚡ ALPHA AI ULTIMATE - POWERED BY DEEPSEEK-R1</div>', unsafe_allow_html=True)

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input: Voice and Text
st.write("---")
col1, col2 = st.columns([1, 4])
with col1:
    v_text = speech_to_text(language='en', start_prompt="🎤 Speak", key='voice_input')
with col2:
    u_input = st.chat_input("Ask Alpha anything...")

final_query = v_text if v_text else u_input

# 8. AI Logic (Thinking + Streaming)
if final_query:
    st.session_state.messages.append({"role": "user", "content": final_query})
    with st.chat_message("user"):
        st.markdown(final_query)

    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        response_placeholder = st.empty()
        
        # Phase 1: Show Alpha's Pro Thinking
        thinking_placeholder.markdown('<div class="thinking-box">Alpha\'s pro thinking... 🧠</div>', unsafe_allow_html=True)
        
        try:
            # Phase 2: Groq Streaming Call
            stream = client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[
                    {"role": "system", "content": "You are Alpha AI. Always reply in the user's language."},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                temperature=temp,
                stream=True,
            )

            full_response = ""
            thinking_placeholder.empty() # Remove thinking box before typing starts
            
            # Stop Generation Checkbox
            stop_gen = st.checkbox("⏹️ Stop Alpha")

            for chunk in stream:
                if stop_gen:
                    full_response += "\n\n*[Generation stopped by user]*"
                    break
                
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    # Typewriter effect
                    response_placeholder.markdown(full_response + "▌")
                    time.sleep(0.005)

            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error: {str(e)}")
