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
st.info("Created by Hasith | Powered by Groq LPU™ & Pollinations AI")

current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

def render_message(role, content):
    with st.chat_message(role):
        image_match = re.search(r'!\[Image\]\((https://pollinations\.ai/p/.*?)\)', content)
        if image_match:
            text_parts = content.split('![Image](')
            text_before = text_parts[0]
            if text_before.strip():
                st.markdown(text_before)
            
            image_url = image_match.group(1)
            try:
                st.image(image_url, use_container_width=True)
            except Exception:
                st.warning("⚠️ Could not display the image.")
                
            st.markdown(f"**🔗 Image Link:** [Click Here]({image_url})")

            if len(text_parts) > 1 and ')' in text_parts[1]:
                text_after = text_parts[1].split(')', 1)[-1]
                if text_after.strip():
                    st.markdown(text_after)
        else:
            st.markdown(content)

for message in current_messages:
    render_message(message["role"], message["content"])

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
except Exception:
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

# --- Input Handling & Logic ---
if prompt := st.chat_input("Message Alpha..."):
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Alpha is thinking..."):
                
                should_generate_image = False
                description = None
                
                # Check for confirmation words in English or Sinhala
                confirmations = ['yes', 'ok', 'sure', 'do it', 'ඔව්', 'හා', 'එල', 'හරි']
                if st.session_state.last_image_request and any(word in prompt.lower() for word in confirmations):
                    should_generate_image = True
                    description = st.session_state.last_image_request
                    st.session_state.last_image_request = None

                image_triggers = ['imagine', 'draw', 'generate image', 'show image', 'අඳින්න', 'මවන්න', 'පින්තූරයක්']
                if not should_generate_image and any(trigger in prompt.lower() for trigger in image_triggers):
                    st.session_state.last_image_request = prompt
                    response_text = "Sir Hasith, shall I create this image for you? Please say 'Yes' or 'No'."
                    st.markdown(response_text)
                    current_messages.append({"role": "assistant", "content": response_text})
                
                elif should_generate_image:
                    system_prompt = (
                        "You are Alpha, a professional Bilingual AI (Sinhala & English). "
                        "Creator: HASITH (14 years old from Bandarawela). "
                        "Always be respectful to Hasith. "
                        "Provide a markdown image link: ![Image](https://pollinations.ai/p/DESCRIPTION?width=1024&height=1024&seed=123). "
                        "The DESCRIPTION in the URL must be in English. "
                        "Respond to the user in the language they used (Sinhala or English)."
                    )
                    
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            *[{"role": m["role"], "content": m["content"]} for m in current_messages]
                        ],
                        model="llama-3.3-70b-versatile",
                    )
                    
                    response_text = chat_completion.choices[0].message.content
                    render_message("assistant", response_text)
                    current_messages.append({"role": "assistant", "content": response_text})

                else:
                    system_prompt = (
                        "You are Alpha, a professional Bilingual AI assistant. "
                        "Creator: HASITH from Bandarawela. Be very respectful to him. "
                        "You can speak perfect Sinhala and English. Respond in the same language as the user. "
                        "Maintain a polite and professional tone."
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
