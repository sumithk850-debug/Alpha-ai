import streamlit as st
from groq import Groq
import sys
from io import StringIO
import base64

# -------------------------
# 1️⃣ Page Configuration
# -------------------------
st.set_page_config(
    page_title="Alpha AI ⚡",
    page_icon="⚡",
    layout="centered",
    menu_items={
        'Get Help': 'https://github.com/hasith/alpha-ai',
        'Report a bug': "https://github.com/hasith/alpha-ai/issues",
        'About': "# Alpha AI. Developed by Hasith. Free AI Assistant with Python Lab, Voice Input, File Upload, Dark/Light mode."
    }
)

# -------------------------
# 2️⃣ Premium Banner Top
# -------------------------
st.markdown("""
<div style="width:100%; padding:10px; background-color:#FFD700; color:#000; border-radius:10px; text-align:center; font-weight:bold; margin-bottom:15px;">
Ultimate Free Version ⚡ | Buy the <a href='https://your-premium-link.com' target='_blank' style='color:#000; text-decoration:underline;'>Premium Version</a> for full features!
</div>
""", unsafe_allow_html=True)

# -------------------------
# 3️⃣ Dark / Light Mode
# -------------------------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

theme_toggle = st.sidebar.checkbox("🌗 Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = theme_toggle

bg_color = "#0e1117" if theme_toggle else "#f9f9f9"
text_color = "#ffffff" if theme_toggle else "#000000"

st.markdown(f"""
<style>
body {{ background-color: {bg_color}; color: {text_color}; }}
.stChatMessage {{ background-color: transparent !important; border: none !important; }}
div.stButton > button {{ background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; transition:0.3s; }}
div.stButton > button:hover {{ border-color:#FFD700; background-color:#252525; }}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 4️⃣ Initialize Messages
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------
# 5️⃣ Connect Groq AI
# -------------------------
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

# -------------------------
# 6️⃣ Sidebar Controls
# -------------------------
with st.sidebar:
    st.title("⚙️ System Control")
    temp_val = st.slider("Logic Precision:", 0.0, 1.0, 0.5)
    presence_penalty = st.slider("Creativity Penalty:", 0.0, 2.0, 0.8)
    frequency_penalty = st.slider("Repetition Penalty:", 0.0, 2.0, 0.8)
    
    st.write("---")
    st.subheader("🐍 Python Lab")
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
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# -------------------------
# 7️⃣ Header
# -------------------------
st.markdown('<h1 style="text-align:center;">Alpha AI ⚡</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;">Free AI Assistant with Python Lab, Voice Input & File Upload | Developed by Hasith</p>', unsafe_allow_html=True)

# -------------------------
# 8️⃣ File Upload Support
# -------------------------
uploaded_file = st.file_uploader("📁 Upload a file (txt/pdf) for analysis:", type=["txt","pdf"])
if uploaded_file:
    file_content = uploaded_file.read().decode("utf-8", errors="ignore")
    st.session_state.messages.append({"role": "user", "content": f"[File Content]: {file_content}"})
    st.success(f"File '{uploaded_file.name}' uploaded successfully and added to chat.")

# -------------------------
# 9️⃣ Voice Input (Simulated)
# -------------------------
st.markdown("🎤 **Voice Input:** Type your speech below (simulate voice input).")
voice_text = st.text_input("Voice Input Text")

# -------------------------
# 10️⃣ Show Chat Messages
# -------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------
# 11️⃣ Chat Input & AI Logic
# -------------------------
user_input = st.chat_input("Ask Alpha anything...")
final_input = voice_text if voice_text else user_input

if final_input:
    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.markdown(final_input)

    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are Alpha AI by Hasith. Friendly, intelligent assistant."}] + st.session_state.messages[-20:],
                temperature=temp_val,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                max_tokens=8192,
                stream=True
            )

            res_area = st.empty()
            full_res = ""
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    full_res += delta.content
                    res_area.markdown(full_res + "▌")
            res_area.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
        except Exception as e:
            st.error(f"AI Connection Error: {e}")
