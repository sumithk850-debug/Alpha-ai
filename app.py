import streamlit as st
from groq import Groq
import base64
import sys
from io import StringIO

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Pro", page_icon="⚡", layout="centered")

# 2. Custom CSS
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
    </style>
    """, unsafe_allow_html=True)

# 3. Branding Header
st.markdown('<h1 class="hasith-header">Alpha AI <span class="hasith-header-lightning">⚡</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hasith-subheader">Created by Hasith | Big Brother & Expert Logic</p>', unsafe_allow_html=True)
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
    st.title("⚙️ Control Panel")
    ai_mode = st.radio("Intelligence Mode:", ["Normal (Big Brother)", "Pro (Expert Vision)"], index=0)
    
    st.write("---")
    st.subheader("🤖 AI Tuning")
    temp_val = st.slider("Creativity (Temperature):", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    max_toks = st.slider("Response Length (Tokens):", min_value=128, max_value=4096, value=1024, step=128)
    
    st.write("---")
    st.subheader("⚡ Code Runner")
    user_code = st.text_area("Write Python code:", height=100, placeholder="print('Hello!')")
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
    uploaded_file = st.file_uploader("📸 Vision Upload", type=["jpg", "jpeg", "png"]) if "Pro" in ai_mode else None
    if st.button("🗑️ Clear Chat History", use_container_width=True):
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
if prompt := st.chat_input(f"Message Alpha..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        spinner_text = "Alpha's Ultra Thinking..." if "Pro" in ai_mode else "Alpha is thinking..."
        
        with st.spinner(spinner_text):
            
            # --- FEATURE: Dynamic Persona Logic ---
            if "Pro" in ai_mode:
                # Expert Persona: Detailed, Technical, Scientific
                system_prompt = (
                    "You are Alpha AI ⚡ (Pro Mode), an elite expert and scientist created by Hasith. "
                    "Your mission is to provide extremely detailed, deep, and comprehensive answers. "
                    "Use technical terms, structured data, and go deep into the logic. "
                    "Always respond in the language used by the user."
                )
            else:
                # Big Brother Persona: Simple, Kind, Brief
                system_prompt = (
                    "You are Alpha AI ⚡ (Normal Mode), acting as Hasith's wise big brother. "
                    "Provide very simple, easy-to-understand, and friendly answers. "
                    "Keep it brief and practical, like a brother giving advice. "
                    "Always respond in the language used by the user."
                )

            if "Pro" in ai_mode and uploaded_file:
                model_name = "llama-3.2-11b-vision-instant"
                base64_image = encode_image(uploaded_file)
                messages_payload = [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
            else:
                model_name = "llama-3.3-70b-versatile"
                messages_payload = [{"role": "system", "content": system_prompt}] + st.session_state.messages

            try:
                completion = client.chat.completions.create(
                    messages=messages_payload, 
                    model=model_name, 
                    temperature=temp_val,
                    max_tokens=max_toks
                )
                response = completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {e}")
