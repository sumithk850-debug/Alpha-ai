import streamlit as st
from groq import Groq
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

# ✅ නිවැරදි කරන ලද Google Search Console Verification කේතය
st.markdown('<meta name="google-site-verification" content="ItvqSJ9OBYMArxGI-WkmQ4yccISMfVQ1gYYOKiUYsBw" />', unsafe_allow_html=True)
# General Meta Description for SEO
st.markdown('<meta name="description" content="Alpha AI by Hasith: Your friendly assistant with built-in Python runner. High intelligence and zero repetition.">', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Custom CSS Styling (Dark Theme)
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
        transition: 0.3s;
    }
    div.stButton > button:hover { border-color: #FFD700; }
    </style>
    """, unsafe_allow_html=True)

# 3. Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. API Client
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Missing GROQ_API_KEY! Please add it to Streamlit Secrets.")
    st.stop()

# 5. Sidebar - Controls & Python Lab
with st.sidebar:
    st.title("⚙️ System Control")
    ai_mode = st.radio("Intelligence Level:", ["Normal", "Pro (Deep Expert)"], index=1)
    
    st.write("---")
    st.subheader("🛠️ Anti-Repetition Tuning")
    # ✅ එකම දේ නැවත කීම පාලනය කරන සැකසුම් (Penalties)
    temp_val = st.slider("Logic Precision:", 0.0, 1.0, 0.4)
    presence_penalty = st.slider("Diversity (Presence):", 0.0, 2.0, 1.2) 
    frequency_penalty = st.slider("Uniqueness (Frequency):", 0.0, 2.0, 1.2)
    
    st.write("---")
    st.subheader("🐍 Python Interpreter")
    py_code = st.text_area("Write Python code here:", height=120, placeholder="print('Hello Alpha')")
    if st.button("🚀 Execute Python"):
        buffer = StringIO()
        sys.stdout = buffer
        try:
            exec(py_code)
            st.code(buffer.getvalue() if buffer.getvalue() else "Executed successfully (No output).", language="text")
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            sys.stdout = sys.__stdout__

    st.write("---")
    if st.button("🗑️ Wipe System Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 6. Header
st.markdown('<h1 class="hasith-header">Alpha AI <span style="color:#FFD700;">⚡</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hasith-tagline">Your Friendly AI Assistant and Python Code Runner | Developed by Hasith</p>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.write("Quick Actions:")
    c1, c2, c3 = st.columns(3)
    with c1: st.button("📝 Summarize")
    with c2: st.button("💡 Deep Dive")
    with c3: st.button("✅ Refine")
st.write("---")

# 7. Chat History Rendering
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 8. Main AI Logic
user_input = st.chat_input("Message Alpha...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        spinner_text = "🧠 Alpha's Ultra Thinking..." if "Pro" in ai_mode else "Normalis Thinking... ⚡"
        with st.spinner(spinner_text):
            try:
                # 🎯 Llama 3.3 70B - High Performance Model
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are Alpha AI by Hasith. Friendly and intelligent. Do not repeat your own sentences. Use fresh words."}] + st.session_state.messages[-15:],
                    temperature=temp_val,
                    presence_penalty=presence_penalty,
                    frequency_penalty=frequency_penalty,
                    max_tokens=4000,
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
            except Exception as e:
                st.error("Connection glitch. Try clearing memory.")
