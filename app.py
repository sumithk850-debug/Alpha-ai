import streamlit as st
from groq import Groq
import base64

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Pro", page_icon="⚡", layout="centered")

# 2. Custom CSS for UI Enhancement
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
        font-size: 20px;
        color: #a0a0a0;
        margin-top: 0px;
        margin-bottom: 20px;
    }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Header Section
st.markdown('<h1 class="hasith-header">Alpha AI <span class="hasith-header-lightning">⚡</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hasith-subheader">Created by Hasith</p>', unsafe_allow_html=True)
st.write("---")

# 4. Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Groq Setup
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

# 6. Sidebar with Model Selector
with st.sidebar:
    st.title("⚙️ Alpha Settings")
    ai_mode = st.radio(
        "Select AI Mode:",
        ["Normal", "Thinking", "Pro"],
        index=0
    )
    st.write("---")
    uploaded_file = st.file_uploader("📸 Upload image", type=["jpg", "jpeg", "png"])
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 7. Helper Function: Encode Image
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# 8. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 9. Main Chat Logic
if prompt := st.chat_input(f"Message Alpha ({ai_mode})..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"Alpha is {ai_mode.lower()}..."):
            
            system_prompt = f"You are Alpha AI ⚡ in {ai_mode} mode. Created by Hasith."

            if uploaded_file:
                # UPDATED VISION MODEL
                model_name = "llama-3.2-11b-vision-instant"
                base64_image = encode_image(uploaded_file)
                messages_payload = [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Hasith says: {prompt}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }]
            else:
                # --- UPDATED MODEL NAMES HERE ---
                if ai_mode == "Thinking":
                    # මෙතන මම අලුත්ම specdec මොඩල් එක දැම්මා
                    model_name = "deepseek-r1-distill-llama-70b-specdec" 
                elif ai_mode == "Pro":
                    model_name = "llama-3.3-70b-versatile"
                else:
                    model_name = "llama-3.3-70b-versatile"
                
                messages_payload = [
                    {"role": "system", "content": system_prompt}
                ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

            try:
                chat_completion = client.chat.completions.create(
                    messages=messages_payload,
                    model=model_name,
                    temperature=0.7
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"API Error: {e}")
