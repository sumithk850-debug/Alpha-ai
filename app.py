import streamlit as st
from groq import Groq
import base64

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI Vision", page_icon="🤖", layout="centered")

# 2. Custom CSS for UI Enhancement
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .hasith-header {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 50px;
        color: #ffffff;
        margin-bottom: 0px;
    }
    .hasith-subheader {
        font-family: 'Montserrat', sans-serif;
        font-size: 18px;
        color: #a0a0a0;
        margin-top: 0px;
        margin-bottom: 20px;
    }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Header Section
st.markdown('<h1 class="hasith-header">Alpha AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="hasith-subheader">Created by Hasith</p>', unsafe_allow_html=True)
st.write("---")

# 4. Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Groq Client Initialization
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("GROQ_API_KEY is missing in Streamlit Secrets.")
    st.stop()

# 6. Sidebar for Tools
with st.sidebar:
    st.title("Settings")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.info("System: Llama-3 Vision Enabled")

# 7. Image Encoding Function
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# 8. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 9. Main Chat Logic
if prompt := st.chat_input("Message Alpha..."):
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            
            # System Instructions (Defined in English for stability)
            system_prompt = (
                "You are Alpha AI, a highly advanced artificial intelligence created by Hasith. "
                "Always treat Hasith with respect. You are intelligent, witty, and helpful. "
                "You can understand and respond in both English and Sinhala accurately."
            )

            # Vision Mode Logic
            if uploaded_file:
                try:
                    base64_image = encode_image(uploaded_file)
                    messages_payload = [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"User (Hasith) says: {prompt}"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }]
                    model = "llama-3.2-11b-vision-preview"
                except Exception as e:
                    st.error(f"Image Error: {e}")
                    st.stop()
            else:
                # Standard Chat Mode
                messages_payload = [
                    {"role": "system", "content": system_prompt}
                ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                model = "llama-3.3-70b-versatile"

            # Execute Request
            try:
                chat_completion = client.chat.completions.create(
                    messages=messages_payload,
                    model=model,
                    temperature=0.7
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"API Error: {e}")
