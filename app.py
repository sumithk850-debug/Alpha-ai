import streamlit as st
from groq import Groq
import sys
from io import StringIO

# ---------------------------------------------------------
# 1. Page Configuration & Analytics
# ---------------------------------------------------------
st.set_page_config(
    page_title="Alpha AI ⚡",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Google Analytics Integration
st.markdown("""
<script async src="https://www.googletagmanager.com/gtag/js?id=G-7YH49L26HC"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-7YH49L26HC');
</script>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Ultra-Digital Cyberpunk UI Styling
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at center, #0a192f 0%, #020617 100%) !important;
        color: #e2e8f0;
    }
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 65px;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(to right, #ffffff, #ffd700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .tagline {
        text-align: center;
        color: #94a3b8;
        font-size: 18px;
        margin-bottom: 30px;
    }
    /* Image Neon Glow Effect */
    .brain-glow img {
        border-radius: 25px;
        box-shadow: 0 0 60px rgba(0, 191, 255, 0.4);
        border: 1px solid rgba(0, 191, 255, 0.2);
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    /* Action Card Styling */
    div.stButton > button {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid #1e293b;
        border-radius: 15px;
        color: #FFD700 !important;
        height: 110px;
        font-size: 18px;
        font-weight: bold;
        transition: 0.4s;
    }
    div.stButton > button:hover {
        border-color: #ffd700;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
        transform: translateY(-5px);
    }
    /* Chat Input Styling */
    .stChatInputContainer {
        border-radius: 20px;
        border: 1px solid #1e293b;
        background: #0f172a !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. Sidebar - Tuning & Developer Tools
# ---------------------------------------------------------
with st.sidebar:
    st.title("⚙️ System Control")
    st.write("---")
    
    # Intelligence Tuning Sliders
    st.subheader("🛠️ Intelligence Tuning")
    temp = st.slider("Logic Precision (Temp):", 0.0, 1.0, 0.4)
    presence_pen = st.slider("Diversity Penalty:", 0.0, 2.0, 1.3)
    freq_pen = st.slider("Repetition Penalty:", 0.0, 2.0, 1.3)
    
    st.write("---")
    
    # Python Lab
    st.subheader("🐍 Python Lab")
    py_code = st.text_area("Write Python code:", height=150)
    if st.button("🚀 Run Python Code", use_container_width=True):
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
    if st.button("🗑️ Wipe Chat Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# 4. Main UI Content
# ---------------------------------------------------------
st.markdown('<h1 class="main-title">Alpha AI ⚡</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Your Friendly AI Assistant & Python Code Runner | Developed by Hasith</p>', unsafe_allow_html=True)

# ✅ පින්තූරය මෙතනින් පෙන්වයි (Local GitHub Image)
st.markdown('<div class="brain-glow">', unsafe_allow_html=True)
try:
    st.image("digital_brain.jpg", use_container_width=True)
except:
    st.error("Error: Please upload 'digital_brain.jpg' to your GitHub repository.")
st.markdown('</div>', unsafe_allow_html=True)

# 5. Quick Actions Section
st.write("### 🚀 Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Summarize\nGet a concise summary"):
        st.session_state.messages.append({"role": "user", "content": "Summarize this topic for me."})
        st.rerun()

with col2:
    if st.button("💡 Deep Dive\nDetailed exploration"):
        st.session_state.messages.append({"role": "user", "content": "Explain this in extreme detail."})
        st.rerun()

with col3:
    if st.button("✅ Refine\nImprove & polish text"):
        st.session_state.messages.append({"role": "user", "content": "Refine and improve this text for me."})
        st.rerun()

st.write("---")

# ---------------------------------------------------------
# 6. Chat Interface & AI Engine
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# API Client Connection
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("GROQ_API_KEY missing in Secrets!")
    st.stop()

user_input = st.chat_input("Ask Alpha anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("AI is thinking..."):
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are Alpha AI, an advanced AI by Hasith."}] + st.session_state.messages[-12:],
                temperature=temp,
                presence_penalty=presence_pen,
                frequency_penalty=freq_pen,
                stream=True
            )
            full_res = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
