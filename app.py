import streamlit as st

st.set_page_config(page_title="Alpha AI", page_icon="🤖", layout="wide")

# ================== CUSTOM CSS ==================
st.markdown("""
<style>

/* ===== MAIN BACKGROUND ===== */
.stApp {
    background: black;
    overflow: hidden;
}

/* ===== MOVING STARS ===== */
.stApp::before {
    content: "";
    position: fixed;
    width: 200%;
    height: 200%;
    background: transparent url('https://www.transparenttextures.com/patterns/stardust.png') repeat;
    animation: moveStars 100s linear infinite;
    opacity: 0.25;
    z-index: 0;
}

@keyframes moveStars {
    from {transform: translate(0,0);}
    to {transform: translate(-500px,-500px);}
}

/* ===== CONTENT LAYER FIX ===== */
.block-container {
    position: relative;
    z-index: 2;
}

/* ===== TITLE ===== */
.alpha-title {
    font-size: 70px;
    font-weight: 900;
    text-align: center;
    color: white;
    margin-bottom: 10px;
}

.alpha-tagline {
    text-align: center;
    font-size: 22px;
    color: white;
    margin-bottom: 40px;
}

/* ===== DIGITAL BRAIN ===== */
.brain {
    width: 300px;
    height: 300px;
    margin: auto;
    border-radius: 50%;
    background: radial-gradient(circle, #00f5ff, #0066ff, #001f3f);
    box-shadow: 0 0 40px #00f5ff,
                0 0 80px #0066ff,
                0 0 120px #00f5ff;
    animation: pulse 3s infinite alternate;
}

@keyframes pulse {
    from {
        transform: scale(1);
    }
    to {
        transform: scale(1.05);
    }
}

/* ===== CHAT BOX STYLE ===== */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.08) !important;
    border-radius: 15px;
    padding: 15px;
    color: white !important;
    font-size: 18px;
}

/* FORCE TEXT WHITE */
[data-testid="stChatMessage"] * {
    color: white !important;
}

/* ===== CHAT INPUT ===== */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.15);
    border-radius: 20px;
}

/* ===== BUTTONS ===== */
div.stButton > button {
    background: linear-gradient(90deg,#00f5ff,#00ffcc);
    color: black;
    font-weight: 700;
    border-radius: 20px;
    border: none;
}

div.stButton > button:hover {
    box-shadow: 0 0 20px #00f5ff;
    transform: scale(1.05);
}

</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown('<div class="alpha-title">Alpha AI ⚡</div>', unsafe_allow_html=True)
st.markdown('<div class="alpha-tagline">Your Friendly AI Assistant & Python Code Runner</div>', unsafe_allow_html=True)
st.markdown('<div class="brain"></div>', unsafe_allow_html=True)

st.write("")

# ================== CHAT SYSTEM ==================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display old messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    response = f"You said: {prompt}"

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
