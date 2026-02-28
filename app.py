import streamlit as st
from groq import Groq
import base64
import sys
from io import StringIO

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Dev", page_icon="⚡", layout="centered")

# 2. Custom CSS for Clean UI
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .hasith-header {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 55px;
        color: #ffffff;
        margin-bottom: 5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .hasith-header-lightning {
        font-size: 55px;
        color: #FFD700;
        margin-left: 10px;
        vertical-align: middle;
    }
    .hasith-subheader {
        font-family: 'Montserrat', sans-serif;
        font-size: 18px;
        color: #a0a0a0;
        margin-bottom: 20px;
    }
    .stChatMessage { background-color: transparent !important; border: none !important; }
    .code-box { background-color: #1e1e1e; padding: 10px; border-radius: 10px; border-left: 5px solid #FFD700; }
    </style>
    """, unsafe_allow_html=True)

# 3. Branding Header
st.markdown('<h1 class="hasith-header">Alpha AI <span class="hasith-header-lightning">⚡</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hasith-subheader">Multi-Language Pro & Code Runner | Created by Hasith</p>', unsafe_allow_html=True)
st.write("---")

# 4. Initialize Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Groq Setup
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# 6. Sidebar
with st.sidebar:
    st.title("⚙️ Alpha Settings")
    ai_mode = st.radio("Mode:", ["Normal (70B)", "Pro (Vision)"], index=0)
    st.write("---")
    
    # Python Code Runner Sidebar Tool
    st.subheader("⚡ Python Interpreter")
    user_code = st.text_area("Write Python code here:", height=150, placeholder="print('Hello Hasith!')")
    if st.button("Run Code"):
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        try:
            exec(user_code)
            sys.stdout = old_stdout
            st.code(redirected_output.getvalue(), language="python")
        except Exception as e:
            sys.stdout = old_stdout
            st.error(f"Error: {e}")
    
    st.write("---")
    uploaded_file = st.file_uploader("📸 Vision Upload", type=["jpg", "jpeg", "png"]) if ai_mode == "Pro (Vision)" else None
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# 7. Image Encoding
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# 8. Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 9. Main AI Logic
if prompt := st.chat_input(f"Message Alpha ({ai_mode})..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Alpha is thinking..."):
            
            # --- FEATURE 5: Polyglot Support Prompt ---
            system_prompt = (
                "You are Alpha AI ⚡, a professional multi-language assistant created by Hasith. "
                "CRITICAL: Always respond in the SAME LANGUAGE as the user's last message. "
                "If user speaks Sinhala, respond in grammatically perfect Sinhala. "
                "If English, respond in professional English. Do not mix languages unless requested."
            )

            if ai_mode == "Pro (Vision)" and uploaded_file:
                model_name = "llama-3.2-11b-vision-instant"
                base64_image = encode_image(uploaded_file)
                messages_payload = [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
            else:
                model_name = "llama-3.3-70b-versatile"
                messages_payload = [{"role": "system", "content": system_prompt}] + st.session_state.messages

            try:
                completion = client.chat.completions.create(messages=messages_payload, model=model_name, temperature=0.5)
                response = completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {e}")
