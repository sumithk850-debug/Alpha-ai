import streamlit as st
from groq import Groq
import sys
from io import StringIO

# ---------------------------------------------------------
# 1. Page Configuration & Analytics Tag
# ---------------------------------------------------------
st.set_page_config(
    page_title="Alpha AI: Your Friendly Assistant",
    page_icon="⚡",
    layout="centered"
)

# ✅
st.markdown("""
<script async src="https://www.googletagmanager.com/gtag/js?id=G-7YH49L26HC"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-7YH49L26HC');
</script>
""", unsafe_allow_html=True)

# Google Search Console Verification Meta Tag
st.markdown('<meta name="google-site-verification" content="ItvqSJ9OBYMArxGI-WkmQ4yccISMfVQ1gYYOKiUYsBw" />', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. UI Styling
# ---------------------------------------------------------
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .h-header { color: #ffffff; text-align: center; font-weight: 700; font-size: 45px; margin-bottom: 20px; }
    div.stButton > button {
        background-color: #1e1e1e;
        color: #FFD700;
        border: 1px solid #30363d;
        border-radius: 12px;
        width: 100%;
        transition: 0.3s;
    }
    div.stButton > button:hover { border-color: #FFD700; background-color: #252525; }
    </style>
    """, unsafe_allow_html=True)

# Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# API Setup
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Missing API Key in Secrets!")
    st.stop()

# 3. Sidebar Tools
with st.sidebar:
    st.title("⚙️ Control Panel")
    if st.button("🗑️ Clear Chat Memory"):
        st.session_state.messages = []
        st.rerun()
    st.write("---")
    st.subheader("🐍 Python Lab")
    py_code = st.text_area("Write Python code:", height=100)
    if st.button("🚀 Run"):
        buffer = StringIO()
        sys.stdout = buffer
        try:
            exec(py_code)
            st.code(buffer.getvalue() if buffer.getvalue() else "Success.", language="text")
        except Exception as e: st.error(f"Error: {e}")
        finally: sys.stdout = sys.__stdout__

# 4. Header & Quick Actions (Summarize, Deep Dive, Refine)
st.markdown('<h1 class="h-header">Alpha AI ⚡</h1>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.write("Quick Actions:")
    col1, col2, col3 = st.columns(3)
    if col1.button("📝 Summarize"):
        st.session_state.messages.append({"role": "user", "content": "Please summarize our discussion so far."})
        st.rerun()
    if col2.button("💡 Deep Dive"):
        st.session_state.messages.append({"role": "user", "content": "Explain the current topic in extreme detail."})
        st.rerun()
    if col3.button("✅ Refine"):
        st.session_state.messages.append({"role": "user", "content": "Improve and polish the last text for me."})
        st.rerun()

st.write("---")

# 5. Chat History & AI Engine
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Message Alpha...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are Alpha AI by Hasith. Intelligent and friendly."}] + st.session_state.messages[-10:],
                stream=True
            )
            full_res = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": full_res})

