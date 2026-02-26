import streamlit as st
from groq import Groq

st.set_page_config(page_title="Alpha AI", page_icon="⚡")

if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"].strip()
    client = Groq(api_key=api_key)
else:
    st.error("GROQ_API_KEY missing in Secrets.")
    st.stop()

st.title("⚡ Alpha AI")
st.caption("Developed by: Hasith from Bandarawela")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Alpha සමඟ කතා කරන්න..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            system_instructions = (
                "You are Alpha AI. Your creator is HASITH, a 14-year-old brilliant mind from Bandarawela. "
                "You must always address Hasith and others with extreme respect (using 'ඔබතුමා', 'ඔබ' and polite Sinhala). "
                "You are an expert in the Sinhala language. Use poetic, clear, and grammatically correct Sinhala. "
                "Always remember your previous conversation history provided in the context."
            )
            
            chat_completion = client.chat.completions.create(
                messages=[{"role": "system", "content": system_instructions}] + [
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
