import streamlit as st
from groq import Groq
import sys
from io import StringIO

# 1. Page Configuration & Analytics
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

# 2. Modern Cyberpunk UI Styling
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
    /* Image Neon Glow */
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
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar - Tuning & Python Tools
with st.sidebar:
    st.title("⚙️ System Control")
    st.write("---")
    
    st.subheader("🛠️ Intelligence Tuning")
    temp = st.slider("Logic Precision (Temp):", 0.0, 1.0, 0.4)
    presence_pen = st.slider("Diversity Penalty:", 0.0, 2.0, 1.3)
    freq_pen = st.slider("Repetition Penalty:", 0.0, 2.0, 1.3)
    
    st.write("---")
    
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

# 4. Header & Your Image
st.markdown('<h1 class="main-title">Alpha AI ⚡</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Your Friendly AI Assistant & Python Code Runner | Developed by Hasith</p>', unsafe_allow_html=True)

# ✅ This links the image file you uploaded to the UI
st.markdown('<div class="brain-glow">', unsafe_allow_html=True)
try:
    # This looks for the "digital_brain.jpg" file you uploaded to GitHub
    st.image("digital_brain.jpg", use_container_width=True)
except:
    st.warning("Please make sure 'digital_brain.jpg' is uploaded to the same folder as app.py in GitHub.")
st.markdown('</div>', unsafe_allow_html=True)

# 5. Quick Actions
st.write("### 🚀 Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Summarize"):
        st.session_state.messages.append({"role": "user", "content": "Please summarize our current topic."})
        st.rerun()
with col2:
    if st.button("💡 Deep Dive"):
        st.session_state.messages.append({"role": "user", "content": "Explain this in extreme detail."})
        st.rerun()
with col3:
    if st.button("✅ Refine"):
        st.session_state.messages.append({"role": "user", "content": "Refine and improve this text for me."})
        st.rerun()

st.write("---")

# 6. AI Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("GROQ_API_KEY is missing!")
    st.stop()

user_input = st.chat_input("Ask Alpha anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are Alpha AI by Hasith."}] + st.session_state.messages[-12:],
            temperature=temp,
            presence_penalty=presence_pen,
            frequency_penalty=freq_pen,
            stream=True
        )
        full_res = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": full_res})
