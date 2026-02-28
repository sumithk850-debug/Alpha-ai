import streamlit as st
from groq import Groq
import base64

# 1. Page Config
st.set_page_config(page_title="Alpha AI Vision", page_icon="👁️", layout="centered")

# 2. Initialize Session
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Groq Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 4. Sidebar
with st.sidebar:
    st.title("🤖 Alpha AI Vision")
    st.write("---")
    st.write("**Owner:** Hasith")
    uploaded_file = st.file_uploader("📸 Upload an image to show Hasith's AI", type=["jpg", "jpeg", "png"])
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# 5. Helper Function: Encode Image to Base64
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# 6. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Chat Logic
if prompt := st.chat_input("Ask Alpha about anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Alpha is looking..."):
            
            # CASE A: Image is uploaded (Vision Mode)
            if uploaded_file:
                base64_image = encode_image(uploaded_file)
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Hasith asks: {prompt}"},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                            },
                        ],
                    }
                ]
                model_name = "llama-3.2-11b-vision-preview"
            
            # CASE B: Normal Text Chat
            else:
                messages = [
                    {"role": "system", "content": "You are Alpha AI created by Hasith. You are brilliant and respectful to Master Hasith."}
                ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                model_name = "llama-3.3-70b-versatile"

            try:
                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model=model_name,
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {e}")
