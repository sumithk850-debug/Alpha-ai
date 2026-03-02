import streamlit as st
from groq import Groq
import sys
from io import StringIO
from PIL import Image

# ---------------------------------------------------------
# 1. Page Config & Analytics
# ---------------------------------------------------------
st.set_page_config(page_title="Alpha AI", page_icon="⚡", layout="wide")

# Google Analytics Tag
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
# 2. Ultra-Digital CSS Styling (Matching your Design)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Main Background with radial gradient */
    .stApp {
        background: radial-gradient(circle at center, #0a192f 0%, #020617 100%) !important;
        color: #e2e8f0;
    }

    /* Digital Header */
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 60px;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(to right, #ffffff, #ffd700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-top: 20px;
    }
    .tagline {
        text-align: center;
        color: #94a3b8;
        font-size: 18px;
        margin-bottom: 30px;
        font-weight: 300;
    }

    /* Input Box Styling */
    .stChatInputContainer {
        border-radius: 20px;
        border: 1px solid #1e293b;
        background: #0f172a !important;
        box-shadow: 0 0 15px rgba(0, 191, 255, 0.1);
    }

    /* Styling for image */
    .digital-brain-img img {
        border-radius: 20px;
        box-shadow: 0 0 40px rgba(0, 191, 255, 0.3) !important; /* నిల్ పాట దిలిసీమ */
        margin-bottom: 40px;
        border: 1px solid rgba(0, 191, 255, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. Sidebar - Tuning & Python Lab
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛠️ Response Tuning")
    temp = st.slider("Logic Precision", 0.0, 1.0, 0.5)
    
    st.write("---")
    st.markdown("### 🐍 Python Interpreter")
    py_code = st.text_area("Write Python code here...", height=150)
    if st.button("🚀 Execute Code", use_container_width=True):
        buffer = StringIO()
        sys.stdout = buffer
        try:
            exec(py_code)
            st.code(buffer.getvalue(), language="text")
        except Exception as e: 
            st.error(f"Error: {e}")
        finally: 
            sys.stdout = sys.__stdout__
    
    st.write("---")
    st.markdown("### 🗑️ Memory Management")
    if st.button("Clear Chat Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# 4. Main UI (Matching the Design)
# ---------------------------------------------------------
st.markdown('<h1 class="main-title">Alpha AI ⚡</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Your Friendly AI Assistant & Python Code Runner | Developed by Hasith</p>', unsafe_allow_html=True)

# ✅ පින්තූරය නිවැරදිව පෙන්වන කොටස
try:
    image = Image.open('digital_brain.png')
    st.image(image, use_container_width=True)
except FileNotFoundError:
    st.error("digital_brain.png not found. Please upload it to your GitHub repository.")
# ... rest of the code ...
