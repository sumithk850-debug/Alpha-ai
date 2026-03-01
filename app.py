import streamlit as st
from groq import Groq
import base64
import sys
from io import StringIO

# ---------------------------------------------------------
# 1. Page Configuration & SEO (Google Search)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Alpha AI: Your Friendly AI Assistant and Python Code Runner",
    page_icon="⚡",
    layout="centered",
    menu_items={
        'Get Help': 'https://github.com/hasith/alpha-ai',
        'About': "# Alpha AI. Developed by Hasith. Friendly & Ultra-Intelligent."
    }
)

# Google Search Console Verification - ඔයාගේ කේතය මෙන්න
st.markdown('<meta name="google-site-verification" content="4b5590848e88e155" />', unsafe_allow_html=True)
# General Meta Description
st.markdown('<meta name="description" content="Alpha AI by Hasith: Friendly assistant with built-in Python runner.">', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Custom CSS Styling
# ---------------------------------------------------------
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .hasith-header {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 50px;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0px;
    }
    .hasith-tagline {
        font-family: 'Montserrat', sans-serif;
        font-size: 16px;
        color: #a0a0a0;
        text-align: center;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .stChatMessage { background-color: transparent !important; border: none !important; }
    div.stButton > button {
        background-color: #1e1e1e;
        color: #FFD700;
        border: 1px solid #30363d;
        border-radius: 12px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Missing GROQ_API_KEY in Secrets!")
    st.stop()

# 4. Sidebar - Controls & Python Lab
with st.sidebar:
    st.title("⚙️ System Control")
    ai_mode = st.radio("Intelligence Level:", ["Normal", "Pro (Deep Expert)"], index=1)
    
    st.write("---")
    st.subheader("🛠️ Anti-Repetition Tuning")
    # මෙහි අගයන් 1.2 ට වඩා වැඩි කර ඇත (එකම දේ කීම වැළැක්වීමට)
    temp_val = st.slider("Logic Precision:", 0.0, 1.0, 0.4)
    presence_penalty = st.slider("Diversity (Presence):", 0.0, 2.0, 1.3) 
    frequency_penalty = st.slider("Uniqueness (Frequency):", 0.0, 2.0, 1.3)
    
    st.write("---")
    st.subheader("🐍 Python Interpreter")
    py_code = st.text_area("Write Python code here:", height=120)
    if st.button("🚀 Execute Python"):
        buffer = StringIO()
        sys.stdout = buffer
        try:
            exec(py_code)
            st.code(buffer.getvalue() if buffer.getvalue() else "Success.", language="text")
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            sys.stdout = sys.__stdout__

    st.write("---")
    if st.button("🗑️ Wipe Memory"):
        st.session_state.messages = []
        st.rerun()

# 5. Header
st.markdown('<h1 class="hasith-header">Alpha AI <span style="color:#FFD700;">⚡</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hasith-tagline">Your Friendly AI Assistant and Python Code Runner | Developed by Hasith</p>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.write("Quick Actions:")
    c1, c2, c3 = st.columns(3)
    with c1: st.button("📝 Summarize")
    with c2: st.button("💡 Deep Dive")
    with c3: st.button("✅ Refine")
st.write("---")

# 6. Chat Rendering
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. AI Logic
user_input = st.chat_input("Message Alpha...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        spinner_text = "🧠 Alpha's Ultra Thinking..." if "Pro" in ai_mode else "Normalis Thinking... ⚡"
        with st.spinner(spinner_text):
            try:
                # Llama 3.3 70B - Ultimate Intelligence
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are Alpha AI by Hasith. Friendly, diverse, and accurate. NEVER repeat phrases."}] + st.session_state.messages[-15:],
                    temperature=temp_val,
                    presence_penalty=presence_penalty,
                    frequency_penalty=frequency_penalty,
                    stream=True
                )
                
                res_box = st.empty()
                full_res = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        res_box.markdown(full_res + "▌")
                
                res_box.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                st.rerun()
            except:
                st.error("Connection lost.")
