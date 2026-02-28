import streamlit as st
from groq import Groq
import base64

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Extreme", page_icon="⚡", layout="centered")

# 2. Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .hasith-header {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 50px;
        color: #ffffff;
        margin-bottom: 0px;
    }
    .hasith-tagline {
        font-family: 'Montserrat', sans-serif;
        font-size: 16px;
        color: #a0a0a0;
        margin-top: -10px;
        margin-bottom: 10px;
    }
    .stChatMessage { background-color: transparent !important; border: none !important; }
    div.stButton > button {
        background-color: #1e1e1e;
        color: #FFD700;
        border: 1px solid #30363d;
        border-radius: 15px;
        font-size: 12px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. API Client Setup
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("API Key not found. Please check your secrets.")
    st.stop()

# 5. Sidebar - Advanced Tuning Panel
with st.sidebar:
    st.title("⚙️ System Control")
    ai_mode = st.radio("Intelligence Mode:", ["Normal", "Pro (Deep Expert)"], index=1)
    
    st.write("---")
    st.subheader("🛠️ Professional Tuning")
    
    # Advanced parameters for better control
    temp_val = st.slider("Temperature (Creativity):", 0.0, 1.0, 0.3 if "Pro" in ai_mode else 0.7, help="Lower is more factual, higher is more creative.")
    top_p_val = st.slider("Top P (Diversity):", 0.0, 1.0, 0.9, help="Controls the range of vocabulary choices.")
    presence_pen = st.slider("Presence Penalty:", -2.0, 2.0, 0.0, help="Encourages new topics in the conversation.")
    frequency_pen = st.slider("Frequency Penalty:", -2.0, 2.0, 0.0, help="Reduces repetition of the same words.")
    
    st.write("---")
    max_output = st.number_input("Max Output Tokens:", 128, 8192, 4096 if "Pro" in ai_mode else 1024)
    context_window = st.slider("Memory Depth (Messages):", 1, 30, 15)
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 6. Header Section
st.markdown('<h1 class="hasith-header">Alpha AI <span style="color:#FFD700;">⚡</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hasith-tagline">Advanced Intelligence Platform | Created by Hasith</p>', unsafe_allow_html=True)

# 7. Quick Tools (Auto-Hide)
quick_prompt = None
if len(st.session_state.messages) == 0:
    st.write("Quick Tools:")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📝 Summarize"): quick_prompt = "Summarize our future conversation."
    with col2:
        if st.button("💡 Explain"): quick_prompt = "Explain topics in great detail."
    with col3:
        if st.button("✅ Grammar"): quick_prompt = "Fix my grammatical errors."
    with col4:
        if st.button("📋 Copy"): st.info("Start chat to use Copy.")
    st.write("---")
else:
    st.write(f"**System Status:** {'🔴 Pro Active' if 'Pro' in ai_mode else '🔵 Normal Active'}")
    st.write("---")

# 8. Render History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 9. Logic & Unstoppable Response
prompt_input = st.chat_input("Message Alpha...")
final_prompt = quick_prompt if quick_prompt else prompt_input

if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    with st.chat_message("assistant"):
        spinner_msg = "🧠 Alpha's Ultra Thinking..." if "Pro" in ai_mode else "Normalis Thinking... ⚡"
        
        with st.spinner(spinner_msg):
            system_instruction = (
                "You are Alpha AI ⚡ (Pro Mode). High precision, deep analysis, 100% complete responses in English." if "Pro" in ai_mode 
                else "You are Alpha AI ⚡ (Normal Mode). Clear and professional English responses."
            )

            try:
                # Streaming with advanced tuning parameters
                completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_instruction}] + st.session_state.messages[-context_window:],
                    model="llama-3.3-70b-versatile",
                    temperature=temp_val,
                    top_p=top_p_val,
                    presence_penalty=presence_pen,
                    frequency_penalty=frequency_pen,
                    max_tokens=max_output,
                    stream=True
                )
                
                res_box = st.empty()
                full_res = ""
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        res_box.markdown(full_res + "▌")
                
                res_box.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                st.rerun()
                
            except Exception as e:
                st.error(f"System Error: {e}")
