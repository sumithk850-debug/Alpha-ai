import streamlit as st
from groq import Groq
import uuid
import re

# 1. Page Config
st.set_page_config(page_title="Alpha AI", page_icon="⚡", layout="centered")

# 2. Initialize Session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None

# 3. Sidebar
with st.sidebar:
    st.title("🤖 Alpha AI")
    st.write("Creator: Hasith")
    if st.button("➕ New Chat"):
        st.session_state.messages = []
        st.session_state.last_prompt = None
        st.rerun()

# 4. Main UI
st.title("💥 Alpha AI")

# 5. Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image_url" in msg:
            st.image(msg["image_url"], use_container_width=True)
            st.caption(f"🔗 Link: {msg['image_url']}")

# 6. Groq Setup
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Please add GROQ_API_KEY to Streamlit Secrets!")
    st.stop()

# 7. User Input Logic
if prompt := st.chat_input("Message Alpha..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check for keywords
    img_triggers = ['imagine', 'draw', 'generate', 'අඳින්න', 'පින්තූරයක්']
    confirms = ['yes', 'ok', 'ඔව්', 'හා', 'හරි']

    with st.chat_message("assistant"):
        # CASE A: User says YES to a previous request
        if st.session_state.last_prompt and any(c in prompt.lower() for c in confirms):
            with st.spinner("Generating High-Quality Image..."):
                # Clean the prompt for the URL
                clean_prompt = re.sub(r'[^a-zA-Z0-9]', ' ', st.session_state.last_prompt)
                image_url = f"https://pollinations.ai/p/{clean_prompt.replace(' ', '%20')}?width=1024&height=1024&model=turbo&nologo=true"
                
                response_text = f"Master Hasith, here is what I imagined for: **{st.session_state.last_prompt}**"
                st.markdown(response_text)
                st.image(image_url, use_container_width=True)
                st.caption(f"🔗 Download Link: {image_url}")
                
                # Save to history
                st.session_state.messages.append({"role": "assistant", "content": response_text, "image_url": image_url})
                st.session_state.last_prompt = None # Reset
        
        # CASE B: User asks for a new image
        elif any(t in prompt.lower() for t in img_triggers):
            st.session_state.last_prompt = prompt
            ask_text = "Master Hasith, I can imagine this for you. Shall I proceed? (Yes/No)"
            st.markdown(ask_text)
            st.session_state.messages.append({"role": "assistant", "content": ask_text})
        
        # CASE C: Normal Chat
        else:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "system", "content": "You are Alpha AI by Hasith. Speak English/Sinhala."}] + 
                         [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                model="llama-3.3-70b-versatile",
            )
            res = chat_completion.choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
