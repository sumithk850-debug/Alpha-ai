import streamlit as st
from groq import Groq

# Page Configuration
st.set_page_config(page_title="Alpha AI", page_icon="⚡")

# Groq API Configuration
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"].strip()
    client = Groq(api_key=api_key)
else:
    st.error("GROQ_API_KEY missing in Streamlit Secrets.")
    st.stop()

st.title("⚡ Alpha AI")
st.caption("Developed by: Hasith")

# Chat History Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Message Alpha..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Using Llama 3 (The best model on Groq)
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                model="llama3-8b-8192",
            )
            response_text = chat_completion.choices[0].message.content
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.error(f"Alpha encountered an error: {e}")
