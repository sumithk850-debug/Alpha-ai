import streamlit as st
from groq import Groq
import base64
import sys
from io import StringIO

# ---------------------------------------------------------
# 1. Page Configuration for Google Search (SEO)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Alpha AI: Your Friendly AI Assistant and Python Code Runner",
    page_icon="⚡",
    layout="centered",
    menu_items={
        'Get Help': 'https://github.com/hasith/alpha-ai',
        'Report a bug': "https://github.com/hasith/alpha-ai/issues",
        'About': "# Alpha AI. Developed by Hasith. Your ultra-intelligent friendly assistant."
    }
)

# 2. Add Meta Description for Search Engines
st.markdown('<meta name="description" content="Alpha AI by Hasith: Your friendly AI assistant and Python code runner. Featuring high-precision logic and seamless code execution.">', unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. Custom CSS Styling
# ---------------------------------------------------------
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

# 4. Initialization & API
if "messages" not in st.session_state:
    st.session_state.messages = []

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Missing GROQ_API_KEY. Please add it to Streamlit Secrets.")
    st.stop()

# 5. Sidebar - Control & Python Lab
with st.sidebar:
    st.title("⚙️ System Control")
    ai_mode = st.radio("Intelligence Level:", ["Normal", "Pro (Deep Expert)"], index=1)
    
    st.write("---")
    st.subheader("🛠️ Intelligence Tuning")
    temp_val = st.slider("Logic Precision:", 0.0, 1.0, 0.3 if "Pro" in ai_mode else 0.6)
    presence_penalty = st.slider("Creativity Penalty:", 0.0, 2.0, 0.8)
    frequency_penalty = st.slider("Repetition Penalty:", 0.0, 2.0, 0.8)
    
    st.write("---")
    st.subheader("🐍 Python Interpreter")
    py_code = st.text_area("Write Python code here:", height=120, placeholder="print('Hello World')")
    if st.button("🚀 Execute Python"):
        buffer = StringIO()
        sys.stdout = buffer
        try:
            exec(py_code)
            st.code(buffer.getvalue() if buffer.getvalue() else "Executed successfully.", language="text")
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            sys.stdout = sys.__stdout__

    st.write("---")
    if st.button("🗑️ Wipe System Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 6. Header Branding
st.markdown('<h1 class="hasith-header">Alpha AI <span style="color:#FFD700;">⚡</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hasith-tagline">Your Friendly AI Assistant and Python Code Runner | Developed by Hasith</p>', unsafe_allow_html=True)

# 7. Quick Tools (Auto-Hide Logic)
quick_prompt = None
if not st.session_state.messages:
    st.write("Quick Actions:")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📝 Summarize"): quick_prompt = "Provide a professional summary of our discussion."
    with c2:
        if st.button("💡 Deep Dive"): quick_prompt = "Explain this topic with scientific precision."
    with c3:
        if st.button("✅ Refine"): quick_prompt = "Check and fix any grammar issues in my message."
    with c4:
        if st.button("📋 Copy Chat"): st.info("Chat is empty.")
else:
    st.write(f"**System Status:** {'🔴 Ultra Deep Intelligence Active' if 'Pro' in ai_mode else '🔵 Friendly Assistant Active'}")

st.write("---")

# 8. Render Chat Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 9. Intelligence Logic
user_input = st.chat_input("Ask Alpha anything...")
final_input = quick_prompt if quick_prompt else user_input

if final_input:
    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.markdown(final_input)

    with st.chat_message("assistant"):
        spinner_msg = "🧠 Alpha's Ultra Thinking..." if "Pro" in ai_mode else "Normalis Thinking... ⚡"
        
        with st.spinner(spinner_msg):
            try:
                # Using Llama 3.3 70B for unmatched IQ
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are Alpha AI by Hasith. You are a friendly, ultra-intelligent assistant. Provide diverse, accurate English responses without repeating yourself."}] + st.session_state.messages[-20:],
                    temperature=temp_val,
                    presence_penalty=presence_penalty,
                    frequency_penalty=frequency_penalty,
                    max_tokens=8192,
                    stream=True
                )
                
                res_area = st.empty()
                full_res = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        res_area.markdown(full_res + "▌")
                
                res_area.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                st.rerun()
            except Exception as e:
                st.error("Connection Error. Please try again.")
