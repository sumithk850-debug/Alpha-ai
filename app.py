import streamlit as st
from PyPDF2 import PdfReader
import time, base64, os, bcrypt
import asyncio, edge_tts

# --- 1. Page Configuration ---
st.set_page_config(page_title="KITT AI | Knight Industries", page_icon="🏎️", layout="wide")

# --- 2. Custom Styling ---
st.markdown("""
    <style>
    .stApp { background: #000000; color: #ffffff; font-family: 'Courier New', Courier, monospace; }

    /* Futuristic Loading Screen */
    .loader-container {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        height: 85vh; background: #000; text-align: center;
    }
    .k-text {
        font-size: 6vw; color: red; text-shadow: 0 0 25px red;
        font-weight: bold; letter-spacing: 6px; margin-bottom: 30px;
        animation: flicker 1.5s infinite alternate;
    }
    @keyframes flicker { 0% {opacity:0.6;} 100% {opacity:1;} }

    .scanner-track {
        width: 400px; height: 18px; background: #111;
        border: 2px solid #333; border-radius: 10px;
        position: relative; overflow: hidden;
    }
    .scanner-light {
        width: 100px; height: 100%;
        background: linear-gradient(90deg, transparent, red, transparent);
        box-shadow: 0 0 20px red;
        position: absolute;
        animation: scan 1.8s infinite alternate ease-in-out;
    }
    @keyframes scan { 0% { left: -10%; } 100% { left: 85%; } }

    .boot-info {
        color: #aaa; font-size: 14px; margin-top: 20px; text-transform: uppercase;
    }

    /* Glass Banner */
    .glass-banner {
        background: rgba(255, 0, 0, 0.08);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 0, 0, 0.3);
        padding: 20px; text-align: center;
        border-radius: 12px;
        box-shadow: 0 4px 30px rgba(255, 0, 0, 0.2);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. Functions ---
def typewriter(text, placeholder):
    full = ""
    for char in text:
        full += char
        placeholder.markdown(full + "▌")
        time.sleep(0.02)
    placeholder.markdown(full)

async def get_voice_data(text):
    VOICE = "en-IE-ConnorNeural"
    communicate = edge_tts.Communicate(text, VOICE)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    duration = len(audio_data) / 15500
    return audio_data, duration

# --- 4. Loading Screen ---
if "loaded" not in st.session_state:
    l_screen = st.empty()
    with l_screen.container():
        st.markdown(f"""
            <div class="loader-container">
                <div class="k-text">KITT SYSTEM BOOT</div>
                <div class="scanner-track"><div class="scanner-light"></div></div>
                <div class="boot-info">
                    MEMORY CHECK: OK | CPU: STABLE | SAT LINK: ONLINE <br>
                    <span style="color:red;">AUTHORIZED OPERATOR: HASITH</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(6)
    st.session_state.loaded = True
    st.rerun()

# --- 5. Security System ---
if "user_db" not in st.session_state:
    st.session_state.user_db = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def register_user(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    st.session_state.user_db[username] = hashed

def authenticate_user(username, password):
    if username in st.session_state.user_db:
        return bcrypt.checkpw(password.encode(), st.session_state.user_db[username])
    return False

if not st.session_state.logged_in:
    st.markdown('<div class="glass-banner"><h1>KITT SECURITY PORTAL</h1></div>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🔐 LOGIN", "📝 REGISTER", "⚡ CREATOR"])
    with t1:
        u = st.text_input("ID").lower()
        p = st.text_input("KEY", type="password")
        if st.button("AUTHENTICATE"):
            if authenticate_user(u, p):
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
    with t2:
        nu = st.text_input("New ID")
        np = st.text_input("New KEY", type="password")
        if st.button("CREATE"):
            register_user(nu, np)
            st.success("User registered successfully!")
    with t3:
        bypass = st.text_input("MASTER KEY", key="bp")
        if st.button("OVERRIDE"):
            if bypass == "Hasith12378":
                st.session_state.logged_in, st.session_state.user = True, "Hasith"
                st.rerun()
    st.stop()

# --- 6. Main Dashboard ---
with st.sidebar:
    st.title("DIAGNOSTICS")
    mode = st.radio("Core", ["Normal Mode", "Pro Mode (GPT OSS)"])
    doc = st.file_uploader("Data Uplink", type=["pdf", "txt"])
    extracted = ""
    if doc:
        if doc.type == "application/pdf":
            reader = PdfReader(doc)
            extracted = "".join([p.extract_text() for p in reader.pages])
        else:
            extracted = doc.getvalue().decode()
        st.subheader("📄 Extracted Data")
        st.text_area("Content", extracted, height=200)
        # AI summary placeholder
        if st.button("Summarize"):
            placeholder = st.empty()
            typewriter("KITT: Processing document summary...", placeholder)
            # Here you can integrate Groq/GPT API for actual summary
            st.success("Summary: Document processed successfully (AI integration placeholder).")

    if st.button("SHUTDOWN"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown(f'<div class="glass-banner">KITT SYSTEM ONLINE | Authorized: {st.session_state.user}</div>', unsafe_allow_html=True)
st.write("Welcome to the Knight Industries dashboard. 🚀")
