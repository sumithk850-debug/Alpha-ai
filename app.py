import streamlit as st
from groq import Groq
import base64
import sys
from io import StringIO

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Extreme", page_icon="⚡", layout="centered")

# 2. Advanced Professional CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .hasith-header {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 50px;
        color: #ffffff;
        margin-bottom: 0px;
        text-align: center;
    }
    .hasith-tagline {
        font-family: 'Montserrat', sans-serif;
        font-size: 16px;
        color: #a0a0a0;
        margin-top: -10px;
        margin-bottom: 20px;
        text-align: center;
    }
    .stChatMessage { background-color: transparent !important; border: none !important; }
    
    /* Sidebar & Button Styling */
    div.stButton > button {
        background-color: #1e1e1e;
        color: #FFD700;
        border: 1px solid #30363d;
        border-radius: 12px;
        font-size: 13px;
        width: 100%;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        border-color: #FFD700;
        background-color: #252525;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. API Client (Using Llama 3.3 70B for Ultra Intelligence)
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("CRITICAL ERROR: GROQ_API_KEY is missing in Streamlit Secrets.")
    st.stop()

# 5. Sidebar - Advanced Intelligence & Python Lab
with st.sidebar:
    st.title("⚙️ System Control")
    ai_mode = st.radio("Intelligence Level:", ["Normal", "Pro (Deep Expert)"], index=1)
    
    st.write("---")
    st.subheader("🛠️ Intelligence Tuning")
    # Optimized values to prevent repetition and maximize logic
    temp_val = st.slider("Logic Precision (Temp):", 0.0, 1.0, 0.3 if "Pro" in ai_mode else 0.6)
    presence_penalty = st.slider("Creativity (Presence):", 0.0, 2.0, 0.8)
    frequency_penalty = st.slider("Vocabulary (Frequency):", 0.0, 2.0, 0.8)
    
    st.write("---")
    st.subheader("🐍 Python Interpreter")
    py_code = st.text_area("Enter Python code to execute:", height=120, placeholder="print(2**10)")
    if st.button("🚀 Execute Python"):
        st.info("Output:")
        buffer = StringIO()
        sys.stdout = buffer
        try:
            exec(py_code)
            st.code(buffer.getvalue() if buffer.getvalue() else "Code executed successfully (No Output).", language="text")
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            sys.stdout = sys.__stdout__

    st.write("---")
    if st.button("🗑️ Wipe System Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 6. Header Branding
st.markdown('<h1 class="hasith-header">Alpha AI <span style="color:#FFD700;">⚡</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hasith-tagline">The Ultra Intelligent Platform | Developed by Hasith</p>', unsafe_allow_html=True)

# 7. Quick Tools (Dynamic Visibility)
quick_prompt = None
if not st.session_state.messages:
    st.write("Select a Quick Action:")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📝 Summarize"): quick_prompt = "Provide a high-level summary of our discussion."
    with c2:
        if st.button("💡 Deep Dive"): quick_prompt = "Analyze this topic with extreme scientific depth."
    with c3:
        if st.button("✅ Refine"): quick_prompt = "Review and fix my input for any grammatical errors."
    with c4:
        if st.button("📋 Copy Chat"): st.info("Chat log is empty.")
    st.write("---")
else:
    st.write(f"**Current Status:** {'🔴 Ultra Deep Intelligence Active' if 'Pro' in ai_mode else '🔵 Balanced Logic Active'}")
    st.write("---")

# 8. Chat Rendering
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 9. Ultra Intelligence Logic
user_input = st.chat_input("Ask Alpha anything...")
final_input = quick_prompt if quick_prompt else user_input

if final_input:
    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.markdown(final_input)

    with st.chat_message("assistant"):
        # Branding based on Hasith's request
        spinner_msg = "🧠 Alpha's Ultra Thinking..." if "Pro" in ai_mode else "Normalis Thinking... ⚡"
        
        with st.spinner(spinner_msg):
            # Strict persona to ensure full, diverse, and intelligent responses
            system_persona = (
                "You are Alpha AI ⚡. You are an elite artificial intelligence. "
                "Instructions: 1. Provide 100% complete, uninterrupted answers. "
                "2. Use advanced vocabulary. 3. NEVER repeat the same sentence. "
                "4. Be accurate and scientifically sound. 5. Respond in English only."
            )

            try:
                # Using the massive 70B model for ultimate IQ
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_persona}] + st.session_state.messages[-20:],
                    temperature=temp_val,
                    presence_penalty=presence_penalty,
                    frequency_penalty=frequency_penalty,
                    max_tokens=8192,
                    stream=True
                )
                
                response_area = st.empty()
                collected_text = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        collected_text += chunk.choices[0].delta.content
                        response_area.markdown(collected_text + "▌")
                
                response_area.markdown(collected_text)
                st.session_state.messages.append({"role": "assistant", "content": collected_text})
                st.rerun()

            except Exception as e:
                st.error("System connection lost. Please try again.")
