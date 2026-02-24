import streamlit as st
from groq import Groq

# Page Configuration
st.set_page_config(page_title="Alpha AI", page_icon="⚡")

# Groq API Configuration
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"].strip()
    client = Groq(api_key=api_key)
else:
    st.error("GROQ_API_KEY missing in Secrets.")
    st.stop()

st.title("⚡ Alpha AI")
st.caption("Developed by: Hasith")

# Chat History Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages
for message in st.session_state.messages:
    if message["role"] != "system": # Hide system instructions from chat
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Message Alpha..."):
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Setting the System Identity
            system_message = {
                "role": "system", 
                "content": "You are Alpha AI. Your creator is HASITH. If anyone asks who made you or who is your creator, always say it is HASITH. Be helpful and polite."
            }
            
            # Sending full history including the system message
            chat_completion = client.chat.completions.create(
                messages=[system_message] + [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                model="llama-3.3-70b-versatile",
            )
            
            response_text = chat_completion.choices[0].message.content
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.error(f"Error: {e}")
