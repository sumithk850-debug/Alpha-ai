import streamlit as st
from groq import Groq
import base64

# 1. Page Config (👁️ Visionicon for Alpha)
st.set_page_config(page_title="Alpha AI Vision", page_icon="👁️", layout="centered")

# 2. Custom CSS to Make it Look Super Professional and Beautiful!
st.markdown("""
    <style>
    /* 🎨 Background Color and Overall Layout */
    .main { background-color: #0e1117; }
    
    /* 🎯 Custom Styled Header and Sub-header */
    .hasith-header {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 55px; /* Big and Bold Alpha AI Title */
        color: #ffffff; /* White Text */
        margin-bottom: 5px; /* Close to Creator Line */
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5); /* Adds Depth */
    }
    .hasith-subheader {
        font-family: 'Montserrat', sans-serif;
        font-weight: 300;
        font-size: 20px; /* Smaller Created By Title */
        color: #a0a0a0; /* Greyish Color */
        margin-top: 0px; /* Minimal Space to Alpha AI Title */
    }
    
    /* 🤖 Chat Messages and Other Elements */
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_manager=True)

# 3. Insert the Beautiful Header Content Here!
# ----------------------------------------------------------------------------------------------------------------------
# 🎯 Here is the beautiful Alpha AI Title and Sub-header with Creator Line:
st.markdown('<h1 class="hasith-header">Alpha AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="hasith-subheader">Created by Hasith</p>', unsafe_allow_html=True)
st.write("---") # ----------------------------------------------------------------------------------------------------------------------

# 4. Initialize Session State (Temporary Memory)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Groq Setup (Vision Brain)
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

# 6. Sidebar (Left Pane) with Branding and Image Uploader
with st.sidebar:
    st.title("🤖 Alpha AI Vision")
    st.write("---")
    st.write("**Owner:** Hasith")
    
    # 📸 The Button to Add Image
    uploaded_file = st.file_uploader("📸 Upload an image to show Hasith's AI", type=["jpg", "jpeg", "png"])
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.info("Vision capability is powered by Llama 3.2 on Groq LPU.")

# 7. Helper Function: Encode Image to Base64 for Groq
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# 8. Display Chat History in Main Window
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 9. Chat Logic and Input
if prompt := st.chat_input("Ask Alpha about anything..."):
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Alpha is thinking..."):
            
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
                model_name = "llama-3.2-11b-vision-preview" # Vision Model
            
            # CASE B: Normal Text Chat
            else:
                messages = [
                    {"role": "system", "content": "You are Alpha AI created by Hasith. Switch naturally based on Hasith's input. You are brilliant and respectful to Master Hasith."}
                ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                model_name = "llama-3.3-70b-versatile" # Powerful Text Model

            try:
                # 🚀 Groq LPU: Fast Inference Request
                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model=model_name,
                    temperature=0.7, # Adds creativity and natural feel
                    max_tokens=2048
                )
                
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Error: {e}")
