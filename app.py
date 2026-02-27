import streamlit as st
from groq import Groq
import uuid
import urllib.parse

# Page Configuration
st.set_page_config(page_title="☯ Alpha AI", page_icon="☯", layout="centered")

# --- Initialize Session States ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

def start_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.all_chats[new_id] = []
    st.session_state.current_chat_id = new_id

if st.session_state.current_chat_id is None:
    start_new_chat()

# --- Sidebar - Chat Management ---
with st.sidebar:
    st.title("🤖 Alpha AI")
    st.write("**Creator:** Hasith")
    
    if st.button("➕ New Chat", use_container_width=True):
        start_new_chat()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🕒 Recent Chats")
    
    for chat_id, messages in st.session_state.all_chats.items():
        if messages:
            first_user_msg = next((m["content"] for m in messages if m["role"] == "user"), "Empty Chat")
            label = f"💬 {first_user_msg[:20]}..."
        else:
            label = "💬 New Chat"
        
        if st.button(label, key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.markdown("---")
    if st.button("🗑 Clear All Chats", use_container_width=True):
        st.session_state.all_chats = {}
        st.session_state.current_chat_id = None
        start_new_chat()
        st.rerun()

# --- Main Interface ---
st.title("💥 Alpha AI")
st.info("Created by Hasith | Powered by Groq LPU™ & Pollinations AI")

current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
except Exception:
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

if prompt := st.chat_input("Ask Alpha to imagine something..."):
    
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Alpha is thinking..."):
                system_prompt = (
                    "You are Alpha, a professional AI assistant created by Hasith. "
                    "Hasith is 14 years old from Bandarawela. Always be respectful to him. "
                    "Respond in simple, polite Sinhala. "
                    "CRITICAL: If the user asks you to 'imagine', 'draw', 'generate an image', or 'show a picture' of something, "
                    "you must generate an image URL using this format: https://pollinations.ai/p/{description}?width=1024&height=1024&seed={random_number}. "
                    "Embed it in Markdown like this: ![Image](URL). "
                    "Describe what you imagined in Sinhala as well."
                )

                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *[{"role": m["role"], "content": m["content"]} for m in current_messages]
                    ],
                    model="llama-3.3-70b-versatile",
                )
                
                response_text = chat_completion.choices[0].message.content
                st.markdown(response_text)
            
        current_messages.append({"role": "assistant", "content": response_text})
        
    except Exception as e:
        st.error(f"Error: {e}")
