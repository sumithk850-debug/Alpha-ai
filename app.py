import streamlit as st
from groq import Groq
import base64

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Extreme", page_icon="⚡", layout="centered")

# 2. Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .hasith-header {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 50px;
        color: #ffffff;
    }
    .stChatMessage { background-color: transparent !important; border: none !important; }
    
    /* Quick Action Buttons */
    div.stButton > button {
        background-color: #1e1e1e;
        color: #FFD700;
        border: 1px solid #30363d;
        border-radius: 20px;
        font-size: 13px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. API Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 5. Sidebar
with st.sidebar:
    st.title("⚙️ System Control")
    ai_mode = st.radio("Intelligence Mode:", ["Normal", "Pro (Deep Expert)"], index=1)
    
    st.write("---")
    st.subheader("🛠️ Professional Tuning")
    temp_val = st.slider("Precision:", 0.0, 1.0, 0.3 if "Pro" in ai_mode else 0.7)
    max_output = 8192 if "Pro" in ai_mode else 2048
    context_window = st.slider("Memory Depth:", 1, 20, 10)
    
    st.write("---")
    uploaded_file = st.file_uploader("📸 Vision (Pro Only)", type=["jpg", "jpeg", "png"]) if "Pro" in ai_mode else None
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 6. Header
st.markdown('<h1 class="hasith-header">Alpha AI <span style="color:#FFD700;">⚡</span></h1>', unsafe_allow_html=True)
st.write(f"**System Status:** {'🔴 Pro Active' if 'Pro' in ai_mode else '🔵 Normal Active'}")
st.write("---")

# 7. Chat Display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. Quick Tools
st.write("Quick Tools:")
col1, col2, col3, col4 = st.columns(4)
quick_prompt = None

with col1:
    if st.button("📝 Summarize"):
        quick_prompt = "Please summarize our conversation."
with col2:
    if st.button("💡 Explain More"):
        quick_prompt = "Explain your previous answer in more detail."
with col3:
    if st.button("✅ Fix Grammar"):
        quick_prompt = "Check my last message for errors."
with col4:
    if st.button("📋 Copy Chat"):
        chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        st.code(chat_text, language="text")

# 9. Logic & Unstoppable Response
prompt_input = st.chat_input("Message Alpha...")
final_prompt = quick_prompt if quick_prompt else prompt_input

if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    with st.chat_message("assistant"):
        # 🎯 Dynamic Thinking Message (FIXED)
        spinner_msg = "🧠 Alpha's Ultra Thinking..." if "Pro" in ai_mode else "Normalis Thinking... ⚡"
        
        with st.spinner(spinner_msg):
            # Strict English Personas
            if "Pro" in ai_mode:
                system_instruction = "You are Alpha AI ⚡ (Pro Mode). High precision, deep scientific analysis, absolute English only."
            else:
                system_instruction = "You are Alpha AI ⚡ (Normal Mode). Professional, clear, and helpful responses in English."

            model = "llama-3.2-11b-vision-instant" if ("Pro" in ai_mode and uploaded_file) else "llama-3.3-70b-versatile"
            
            # Payload
            if "Pro" in ai_mode and uploaded_file:
                img_data = base64.b64encode(uploaded_file.read()).decode()
                payload = [{"role": "user", "content": [{"type": "text", "text": final_prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}}]}]
            else:
                payload = [{"role": "system", "content": system_instruction}] + st.session_state.messages[-context_window:]

            try:
                # Streaming for full response
                completion = client.chat.completions.create(
                    messages=payload,
                    model=model,
                    temperature=temp_val,
                    max_tokens=max_output,
                    stream=True
                )
                
                res_box = st.empty()
                full_res = ""
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        res_box.markdown(full_res + "▌")
                
                res_box.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                
            except Exception as e:
                st.error(f"Error: {e}")
