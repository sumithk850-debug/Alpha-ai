import streamlit as st
from groq import Groq
import sys
from io import StringIO

# -------------------------
# 1️⃣ Page Configuration
# -------------------------
st.set_page_config(
    page_title="Alpha AI ⚡ Free",
    page_icon="⚡",
    layout="centered",
    menu_items={
        'Get Help': 'https://github.com/hasith/alpha-ai',
        'Report a bug': "https://github.com/hasith/alpha-ai/issues",
        'About': "# Alpha AI Free Version. Developed by Hasith."
    }
)

# -------------------------
# 2️⃣ Premium Banner Top
# -------------------------
st.markdown("""
<div style="width:100%; padding:10px; background-color:#FFD700; color:#000; border-radius:10px; text-align:center; font-weight:bold; margin-bottom:15px;">
Ultimate Free Version ⚡ | Buy the <a href='https://your-premium-page.com' target='_blank' style='color:#000; text-decoration:underline;'>Premium Version</a> for full features!
</div>
""", unsafe_allow_html=True)

# -------------------------
# 3️⃣ Dark / Light Toggle
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
# 6️⃣ Sidebar Python Lab
# -------------------------
with st.sidebar:
    st.title("🐍 Python Lab")
    py_code = st.text_area("Write Python code here:", height=120, placeholder="print('Hello World')")
    if st.button("🚀 Run Python"):
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
st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ Free</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;">Friendly AI Assistant | Developed by Hasith</p>', unsafe_allow_html=True)

# -------------------------
# 8️⃣ Quick Chat Buttons
# -------------------------
st.write("Quick Actions:")
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("📝 Summarize"):
        quick_prompt = "Provide a professional summary of the topic."
        st.session_state.messages.append({"role":"user","content":quick_prompt})
with c2:
    if st.button("💡 Deep Dive"):
        quick_prompt = "Explain this topic with full details."
        st.session_state.messages.append({"role":"user","content":quick_prompt})
with c3:
    if st.button("✅ Refine"):
        quick_prompt = "Check and improve grammar and clarity."
        st.session_state.messages.append({"role":"user","content":quick_prompt})

# -------------------------
# 9️⃣ Display Chat Messages
# -------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------
# 10️⃣ Chat Input & AI Logic (Spinner, Full Response)
# -------------------------
user_input = st.chat_input("Ask Alpha anything...")
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("🧠 Alpha is thinking..."):
            try:
                # Get full response at once, no streaming
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role":"system","content":"You are Alpha AI by Hasith. Friendly, intelligent assistant."}] + st.session_state.messages[-20:],
                    temperature=0.5,
                    presence_penalty=0.8,
                    frequency_penalty=0.8,
                    max_tokens=4096,
                    stream=False
                )

                full_res = response.choices[0].message.content

                # Remove repetition
                lines = full_res.split("\n")
                deduped = []
                for line in lines:
                    if not deduped or line.strip() != deduped[-1].strip():
                        deduped.append(line)
                full_res = "\n".join(deduped)

                st.markdown(full_res)
                st.session_state.messages.append({"role":"assistant","content":full_res})

            except Exception as e:
                st.error(f"AI Connection Error: {e}")
