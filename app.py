import streamlit as st
from groq import Groq
import sys
from io import StringIO

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Alpha AI ⚡ | Friendly AI Assistant",
    page_icon="⚡",
    layout="centered"
)

# -------------------------------------------------
# FUTURISTIC CSS + ANIMATED DIGITAL BRAIN
# -------------------------------------------------
st.markdown("""
<style>

/* ===== BACKGROUND ===== */
.stApp {
    background: radial-gradient(circle at top, #0c0f1a, #05060d 70%);
    color: white;
}

/* ===== TITLE ===== */
.alpha-title {
    font-size: 65px;
    font-weight: 900;
    text-align: center;
    color: white;
    margin-bottom: 10px;
}

.alpha-tagline {
    text-align: center;
    font-size: 20px;
    color: #cfcfcf;
    margin-bottom: 30px;
}

/* ===== DIGITAL BRAIN ===== */
.brain {
    width: 260px;
    height: 260px;
    margin: 30px auto;
    border-radius: 50%;
    background: radial-gradient(circle, #00f5ff, #0066ff, #001f3f);
    box-shadow: 0 0 40px #00f5ff,
                0 0 80px #0066ff,
                0 0 120px #00f5ff;
    animation: pulse 3s infinite alternate;
}

@keyframes pulse {
    from {
        transform: scale(1);
        box-shadow: 0 0 40px #00f5ff,
                    0 0 80px #0066ff;
    }
    to {
        transform: scale(1.07);
        box-shadow: 0 0 70px #00f5ff,
                    0 0 140px #00ccff;
    }
}

/* ===== GLASS CARDS ===== */
.glass-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.1);
    text-align:center;
    margin-bottom:15px;
}

/* ===== CHAT VISIBILITY FIX ===== */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.06);
    border-radius: 15px;
    padding: 12px;
    color: #ffffff !important;
}

/* ===== BUTTONS ===== */
div.stButton > button {
    background: linear-gradient(90deg,#00f5ff,#00ffcc);
    color: black;
    font-weight: 700;
    border-radius: 20px;
    border: none;
}

div.stButton > button:hover {
    box-shadow: 0 0 20px #00f5ff;
    transform: scale(1.05);
}

/* ===== CHAT INPUT ===== */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.1);
    border-radius: 20px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# GROQ CLIENT
# -------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.title("⚙️ System Control")

    ai_mode = st.radio("Mode:", ["Normal", "Pro"], index=1)

    temp_val = st.slider("Logic Precision", 0.0, 1.0, 0.3)
    presence_penalty = st.slider("Creativity Penalty", 0.0, 2.0, 0.8)
    frequency_penalty = st.slider("Repetition Penalty", 0.0, 2.0, 0.8)

    st.write("---")
    st.subheader("🐍 Python Lab")

    py_code = st.text_area("Run Python Code:", height=120)

    if st.button("🚀 Execute Python"):
        buffer = StringIO()
        sys.stdout = buffer
        try:
            exec(py_code)
            st.code(buffer.getvalue() if buffer.getvalue() else "Executed Successfully.")
        except Exception as e:
            st.error(e)
        finally:
            sys.stdout = sys.__stdout__

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# -------------------------------------------------
# HERO SECTION
# -------------------------------------------------
st.markdown('<div class="alpha-title">Alpha AI ⚡</div>', unsafe_allow_html=True)
st.markdown('<div class="alpha-tagline">Your Friendly AI Assistant & Python Code Runner<br>Developed by Hasith</div>', unsafe_allow_html=True)
st.markdown('<div class="brain"></div>', unsafe_allow_html=True)

# -------------------------------------------------
# QUICK ACTIONS
# -------------------------------------------------
quick_prompt = None

if not st.session_state.messages:

    st.markdown("## 🚀 Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="glass-card">📝 <b>Summarize</b><br>Get concise summary instantly.</div>', unsafe_allow_html=True)
        if st.button("Run Summarizer"):
            quick_prompt = "Provide a professional summary."

    with col2:
        st.markdown('<div class="glass-card">💡 <b>Deep Dive</b><br>Explore deeply with examples.</div>', unsafe_allow_html=True)
        if st.button("Run Deep Dive"):
            quick_prompt = "Explain deeply with examples."

    with col3:
        st.markdown('<div class="glass-card">✅ <b>Refine</b><br>Improve grammar & clarity.</div>', unsafe_allow_html=True)
        if st.button("Run Refiner"):
            quick_prompt = "Fix grammar and improve clarity."

else:
    st.success("🟢 Alpha AI Online")

st.write("---")

# -------------------------------------------------
# DISPLAY CHAT
# -------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------------------------
# CHAT INPUT
# -------------------------------------------------
user_input = st.chat_input("Ask Alpha anything...")
final_input = quick_prompt if quick_prompt else user_input

if final_input:
    st.session_state.messages.append({"role": "user", "content": final_input})

    with st.chat_message("user"):
        st.markdown(final_input)

    with st.chat_message("assistant"):
        with st.spinner("🧠 Alpha Thinking..."):
            try:
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are Alpha AI by Hasith. Be intelligent, friendly and precise."}
                    ] + st.session_state.messages[-20:],
                    temperature=temp_val,
                    presence_penalty=presence_penalty,
                    frequency_penalty=frequency_penalty,
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

            except Exception:
                st.error("Connection Error. Try again.")
