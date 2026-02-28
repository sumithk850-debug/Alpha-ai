import streamlit as st
from groq import Groq
import uuid
import re

# Page Configuration
st.set_page_config(page_title="Alpha AI", page_icon="⚡", layout="centered")

# --- Initialize Session States ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "last_image_request" not in st.session_state:
    st.session_state.last_image_request = None

def start_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.all_chats[new_id] = []
    st.session_state.current_chat_id = new_id
    st.session_state.last_image_request = None

if st.session_state.current_chat_id is None:
    start_new_chat()

# --- Sidebar ---
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

# --- Main Interface ---
st.title("💥 Alpha AI")
st.info("Created by Hasith | Powered by Groq & Pollinations AI")

current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

def render_message(role, content):
    with st.chat_message(role):
        image_match = re.search(r'!\[Image\]\((https://pollinations\.ai/p/.*?)\)', content)
        if image_match:
            parts = content.split('![Image](')
            text_before = parts[0].strip()
            if text_before:
                st.markdown(text_before)
            
            image_url = image_match.group(1).split(')')[0]
            st.image(image_url, use_container_width=True)
            st.markdown(f"**🔗 Download/Link:** [Click Here]({image_url})")
        else:
            st.markdown(content)

for message in current_messages:
    render_message(message["role"], message["content"])

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("API Key missing.")
    st.stop()

if prompt := st.chat_input("Message Alpha..."):
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Alpha is processing..."):
                
                confirms = ['yes', 'ok', 'sure', 'do it', 'ඔව්', 'හා', 'හරි']
                is_confirmation = st.session_state.last_image_request and any(c in prompt.lower() for c in confirms)
                
                triggers = ['imagine', 'draw', 'generate', 'show image', 'පින්තූරයක්', 'අඳින්න', 'picture']
                is_direct_request = any(t in prompt.lower() for t in triggers)

                if is_confirmation:
                    description = st.session_state.last_image_request
                    st.session_state.last_image_request = None
                    sys_msg = (
                        "You are Alpha. Your creator is HASITH. "
                        "IMPORTANT: You MUST generate an image now because the user said YES. "
                        "Format: ![Image](https://pollinations.ai/p/ENGLISH_PROMPT?width=1024&height=1024&seed=123)"
                    )
                elif is_direct_request:
                    st.session_state.last_image_request = prompt
                    response_text = "Master Hasith, I can imagine this for you. Shall I proceed? (Yes/No)"
                    st.markdown(response_text)
                    current_messages.append({"role": "assistant", "content": response_text})
                    st.stop()
                else:
                    sys_msg = "You are Alpha AI, created by HASITH. Be helpful and polite in English or Sinhala."

                if not is_direct_request or is_confirmation:
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "system", "content": sys_msg}] + 
                                 [{"role": m["role"], "content": m["content"]} for m in current_messages],
                        model="llama-3.3-70b-versatile",
                    )
                    res = chat_completion.choices[0].message.content
                    render_message("assistant", res)
                    current_messages.append({"role": "assistant", "content": res})

    except Exception as e:
        st.error(f"Error: {e}")
            
