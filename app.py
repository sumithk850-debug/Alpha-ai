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
# FUTURISTIC CSS
# -------------------------------------------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: radial-gradient(circle at top, #0f2027, #0b0c10 60%);
    color: white;
}

/* Header */
.alpha-title {
    font-size: 60px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg,#ffffff,#00f5ff,#FFD700);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.alpha-tagline {
    text-align: center;
    color: #b0b0b0;
    font-size: 18px;
    margin-bottom: 40px;
}

/* Glass Cards */
.glass-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.1);
    transition: 0.3s;
    text-align:center;
}

.glass-card:hover {
    transform: translateY(-5px);
    border-color: #00f5ff;
    box-shadow: 0 0 20px rgba(0,245,255,0.3);
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(90deg,#00f5ff,#FFD700);
    color: black;
    border-radius: 15px;
    font-weight: 600;
    border: none;
    transition: 0.3s;
}

div.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 15px #00f5ff;
}

/* Chat input */
[data-testid="stChatInput"] {
    border-radius: 20px;
    background: rgba(255,255,255,0.08);
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
    st.error("Add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

# -------------------------------------------------
# SIDEBAR CONTROL PANEL
# -------------------------------------------------
with st.sidebar:
    st.title("⚙️ System Control")

    ai_mode = st.radio("Intelligence Level:", ["Normal", "Pro (Deep Expert)"], index=1)

    st.subheader("🛠️ Intelligence Tuning")
    temp_val = st.slider("Logic Precision:", 0.0, 1.0, 0.3)
    presence_penalty = st.slider("Creativity Penalty:", 0.0, 2.0, 0.8)
    frequency_penalty = st.slider("Repetition Penalty:", 0.0, 2.0, 0.8)

    st.write("---")
    st.subheader("🐍 Python Interpreter")

    py_code = st.text_area("Write Python code:", height=120)

    if st.button("🚀 Execute Python"):
        buffer = StringIO()
        sys.stdout = buffer
        try:
            exec(py_code)
            st.code(buffer.getvalue() if buffer.getvalue() else "Executed successfully.")
        except Exception as e:
            st.error(e)
        finally:
            sys.stdout = sys.__stdout__

    if st.button("🗑️ Clear Memory"):
        st.session_state.messages = []
        st.rerun()

# -------------------------------------------------
# HERO SECTION
# -------------------------------------------------
st.markdown('<div class="alpha-title">Alpha AI ⚡</div>', unsafe_allow_html=True)
st.markdown('<div class="alpha-tagline">Your Friendly AI Assistant & Python Code Runner | Developed by Hasith</div>', unsafe_allow_html=True)

# -------------------------------------------------
# QUICK ACTIONS
# -------------------------------------------------
quick_prompt = None

if not st.session_state.messages:

    st.markdown("## 🚀 Quick Actions")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown('<div class="glass-card">📝 <b>Summarize</b><br>Get concise summary instantly.</div>', unsafe_allow_html=True)
        if st.button("Run Summarizer"):
            quick_prompt = "Provide a professional summary."

    with c2:
        st.markdown('<div class="glass-card">💡 <b>Deep Dive</b><br>Explore topic deeply.</div>', unsafe_allow_html=True)
        if st.button("Run Deep Dive"):
            quick_prompt = "Explain this topic scientifically."

    with c3:
        st.markdown('<div class="glass-card">✅ <b>Refine</b><br>Improve grammar & clarity.</div>', unsafe_allow_html=True)
        if st.button("Run Refiner"):
            quick_prompt = "Fix grammar and improve clarity."

else:
    st.success("🟢 Alpha AI Online")

st.write("---")

# -------------------------------------------------
# CHAT DISPLAY
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
                st.error("Connection error. Try again.")
