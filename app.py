import streamlit as st
from groq import Groq
import sys
from io import StringIO

# ---------------------------------------------------------
# 1. Page Configuration & SEO
# ---------------------------------------------------------
st.set_page_config(
    page_title="Alpha AI: Your Friendly AI Assistant and Python Code Runner",
    page_icon="⚡",
    layout="centered"
)

# ✅ Google Search Console Verification Tag
st.markdown('<meta name="google-site-verification" content="ItvqSJ9OBYMArxGI-WkmQ4yccISMfVQ1gYYOKiUYsBw" />', unsafe_allow_html=True)

# SEO Meta Description
st.markdown('<meta name="description" content="Alpha AI by Hasith: Your ultra-intelligent friendly assistant and Python runner. Features high-speed logic and zero repetition.">', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Professional UI Styling (Dark Mode)
# ---------------------------------------------------------
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .hasith-header {
        font-family: 'Montserrat', sans-serif;
        color: #ffffff;
        text-align: center;
        font-weight: 700;
        font-size: 45px;
        margin-bottom: 0px;
    }
    .hasith-tagline {
        font-family: 'Montserrat', sans-serif;
        color: #a0a0a0;
        text-align: center;
        font-size: 15px;
        margin-top: -10px;
        margin-bottom: 25px;
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
    div.stButton > button:hover {
        border-color: #FFD700;
        background-color: #252525;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Session Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. API Setup
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("CRITICAL ERROR: GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

# 5. Sidebar - AI Controls & Python Lab
with st.sidebar:
    st.title("⚙️ System Control")
    ai_mode = st.radio("Intelligence Mode:", ["Normal", "Pro (Deep Expert)"], index=1)
    
    st.write("---")
    st.subheader("🛠️ Anti-Repetition Tuning")
    # ✅ Optimized penalties to stop Alpha from repeating the same sentences
    temp_val = st.slider("Logic Precision:", 0.0, 1.0, 0.4)
    presence_pen = st.slider("Vocabulary Diversity:", 0.0, 2.0, 1.3)
    freq_pen = st.slider("Sentence Uniqueness:", 0.0, 2.0, 1.3)
    
    st.write("---")
    st.subheader("🐍 Python Interpreter")
    py_code = st.text_area("Write Python code:", height=120, placeholder="print('Alpha is Online')")
    if st.button("🚀 Run Python Code"):
        st.info("Execution Output:")
        buffer = StringIO()
        sys.stdout = buffer
        try:
            exec(py_code)
            st.code(buffer.getvalue() if buffer.getvalue() else "Code executed successfully.", language="text")
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            sys.stdout = sys.__stdout__

    st.write("---")
    if st.button("🗑️ Wipe Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 6. Main Branding
st.markdown('<h1 class="hasith-header">Alpha AI <span style="color:#FFD700;">⚡</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hasith-tagline">Your Friendly AI Assistant and Python Code Runner | Developed by Hasith</p>', unsafe_allow_html=True)

# 7. Dynamic UI (Quick Tools)
if not st.session_state.messages:
    st.write("Quick Tools:")
    c1, c2, c3 = st.columns(3)
    with c1: st.button("📝 Summarize")
    with c2: st.button("💡 Deep Dive")
    with c3: st.button("✅ Refine")
else:
    status = "🔴 Pro Intelligence Active" if "Pro" in ai_mode else "🔵 Friendly Mode Active"
    st.write(f"**Status:** {status}")

st.write("---")

# 8. Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 9. AI Logic (Llama 3.3 70B)
user_input = st.chat_input("Message Alpha...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        thinking_text = "🧠 Alpha's Ultra Thinking..." if "Pro" in ai_mode else "Normalis Thinking... ⚡"
        with st.spinner(thinking_text):
            try:
                # High-IQ Large Language Model
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{
                        "role": "system", 
                        "content": "You are Alpha AI by Hasith. You are friendly and ultra-intelligent. NEVER repeat the same sentences. Use unique words and high-quality English."
                    }] + st.session_state.messages[-15:],
                    temperature=temp_val,
                    presence_penalty=presence_pen,
                    frequency_penalty=freq_pen,
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
                
            except Exception:
                st.error("Connection glitch. Please refresh or clear memory.")
