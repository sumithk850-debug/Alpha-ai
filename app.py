import streamlit as st
from groq import Groq
import uuid
import re
import shelve  

# Page Config
st.set_page_config(page_title="Alpha AI", page_icon="⚡", layout="centered")

# --- Database functions ---
def load_chats():
    with shelve.open("chat_db") as db:
        return db.get("all_chats", {})

def save_chats(chats):
    with shelve.open("chat_db") as db:
        db["all_chats"] = chats

# --- Load data from Database ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_chats()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "last_image_request" not in st.session_state:
    st.session_state.last_image_request = None

def start_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.all_chats[new_id] = []
    st.session_state.current_chat_id = new_id
    save_chats(st.session_state.all_chats)

if st.session_state.current_chat_id is None:
    if st.session_state.all_chats:
        st.session_state.current_chat_id = list(st.session_state.all_chats.keys())[0]
    else:
        start_new_chat()

# Sidebar
with st.sidebar:
    st.title("🤖 Alpha AI")
    st.write("**Creator:** Hasith")
    if st.button("➕ New Chat", use_container_width=True):
        start_new_chat()
        st.rerun()
    st.markdown("---")
    for chat_id, messages in st.session_state.all_chats.items():
        label = f"💬 {messages[0]['content'][:20]}..." if messages else "💬 New Chat"
        if st.button(label, key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

# Main UI
st.title("💥 Alpha AI")
st.info("Created by Hasith | Chats are now permanently saved!")

current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

def display_msg(role, content):
    with st.chat_message(role):
        image_match = re.search(r'!\[Image\]\((https://pollinations\.ai/p/.*?)\)', content)
        if image_match:
            text_before = content.split('![Image]')[0].strip()
            if text_before: st.markdown(text_before)
            img_url = image_match.group(1).split(')')[0]
            st.image(img_url, use_container_width=True)
            st.markdown(f"**🔗 Link:** [Open Image]({img_url})")
        else:
            st.markdown(content)

for msg in current_messages:
    display_msg(msg["role"], msg["content"])

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Key Error")
    st.stop()

if prompt := st.chat_input("Message Alpha..."):
    current_messages.append({"role": "user", "content": prompt})
    save_chats(st.session_state.all_chats) # වහාම සේව් කරන්න
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        confirms = ['yes', 'ok', 'sure', 'do it', 'ඔව්', 'හා', 'හරි']
        triggers = ['imagine', 'draw', 'generate', 'show image', 'පින්තූරයක්', 'අඳින්න']
        
        is_confirm = st.session_state.last_image_request and any(c in prompt.lower() for c in confirms)
        is_request = any(t in prompt.lower() for t in triggers)

        with st.spinner("Alpha is thinking..."):
            if is_confirm:
                desc = st.session_state.last_image_request
                st.session_state.last_image_request = None
                sys_msg = f"Generate an image of: {desc}. Use format: ![Image](https://pollinations.ai/p/PROMPT?width=1024&height=1024&seed=123)"
            elif is_request:
                st.session_state.last_image_request = prompt
                res_text = "Master Hasith, shall I imagine this? (Yes/No)"
                display_msg("assistant", res_text)
                current_messages.append({"role": "assistant", "content": res_text})
                save_chats(st.session_state.all_chats)
                st.stop()
            else:
                sys_msg = "You are Alpha AI created by HASITH. Be polite and helpful."

            chat_completion = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + 
                         [{"role": m["role"], "content": m["content"]} for m in current_messages],
                model="llama-3.3-70b-versatile",
            )
            response = chat_completion.choices[0].message.content
            display_msg("assistant", response)
            current_messages.append({"role": "assistant", "content": response})
            save_chats(st.session_state.all_chats) # පිළිතුරත් සේව් කරන්න

    except Exception as e:
        st.error(f"Error: {e}")
