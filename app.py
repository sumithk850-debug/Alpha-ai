import streamlit as st
from groq import Groq
import time, base64, asyncio, requests, webbrowser, json, os
import edge_tts
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from streamlit_mic_recorder import mic_recorder
from email_validator import validate_email
import streamlit.components.v1 as components

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(page_title="Alpha AI | Jarvis v4", page_icon="⚡", layout="wide")

# -----------------------
# COOKIE LOGIN SYSTEM
# -----------------------
COOKIE_FILE = "alpha_user.json"

def save_user(user):
    with open(COOKIE_FILE,"w") as f:
        json.dump(user,f)

def load_user():
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE) as f:
            return json.load(f)
    return None

def logout():
    if os.path.exists(COOKIE_FILE):
        os.remove(COOKIE_FILE)
    st.session_state.logged_in=False

saved_user = load_user()

# -----------------------
# SESSION STATE
# -----------------------
if "messages" not in st.session_state:
    st.session_state.messages=[]

if "memory" not in st.session_state:
    st.session_state.memory=[]

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

if "user_full_name" not in st.session_state:
    st.session_state.user_full_name=None

# AUTO LOGIN
if saved_user:
    st.session_state.logged_in=True
    st.session_state.user_full_name=saved_user["name"]

# -----------------------
# LOGIN PAGE
# -----------------------
if not st.session_state.logged_in:

    st.title("⚡ ALPHA CORE LOGIN")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1,col2,col3 = st.columns(3)

    with col1:
        if st.button("REGISTER"):
            if name and email and password:
                try:
                    validate_email(email)
                    save_user({"name":name,"email":email})
                    st.session_state.logged_in=True
                    st.session_state.user_full_name=name
                    st.rerun()
                except:
                    st.error("Invalid Email")

    with col2:
        if st.button("LOGIN"):
            if password=="Hasith12378":
                save_user({"name":name,"email":email})
                st.session_state.logged_in=True
                st.session_state.user_full_name=name
                st.rerun()

    with col3:
        if st.button("Sign in with Google"):
            st.info("Google OAuth setup required in Google Cloud Console")

    st.stop()

# -----------------------
# AI CORE FUNCTIONS
# -----------------------
async def speak_alpha(text):
    voice="en-US-SteffanNeural"
    comm=edge_tts.Communicate(text,voice)

    audio=b""
    async for chunk in comm.stream():
        if chunk["type"]=="audio":
            audio+=chunk["data"]

    b64=base64.b64encode(audio).decode()
    st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)

def internet_search(query):
    url=f"https://www.google.com/search?q={query}"
    headers={"User-Agent":"Mozilla/5.0"}
    r=requests.get(url,headers=headers)

    soup=BeautifulSoup(r.text,"html.parser")
    results=[g.text for g in soup.select("div.BNeawe")[:5]]

    return "\n".join(results)

client=Groq(api_key=st.secrets["GROQ_API_KEY"])

def ask_ai(prompt,mode):

    memory="\n".join(st.session_state.memory[-5:])

    if mode=="Normal":
        model="llama-3.3-70b-versatile"
    else:
        model="openai/gpt-oss-120b"

    messages=[
        {"role":"system","content":"You are Alpha AI created by Hasith."},
        {"role":"system","content":memory},
        {"role":"user","content":prompt}
    ]

    res=client.chat.completions.create(
        model=model,
        messages=messages
    )

    return res.choices[0].message.content

# -----------------------
# SIDEBAR CONTROL PANEL
# -----------------------
with st.sidebar:

    st.header("⚡ Alpha Control")

    st.write(f"Operator: **{st.session_state.user_full_name}**")

    # AI MODE SLIDER
    power = st.slider("AI Power Level",0,1,0)

    if power==0:
        mode="Normal"
        st.caption("⚡ LLaMA 70B Fast Mode")
    else:
        mode="Pro"
        st.caption("🚀 GPT 120B Ultra Mode")

    voice_mode=st.checkbox("Voice Chat")
    internet_mode=st.checkbox("Internet Access")

    if st.button("Logout"):
        logout()
        st.rerun()

# -----------------------
# MAIN INTERFACE
# -----------------------
st.title(f"Welcome {st.session_state.user_full_name}")

st.write("Alpha AI ready...")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask Alpha...")

if user_input:

    st.session_state.messages.append({"role":"user","content":user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        if internet_mode:
            prompt=user_input+"\n\nInternet Data:\n"+internet_search(user_input)
        else:
            prompt=user_input

        with st.spinner("Thinking..."):
            answer=ask_ai(prompt,mode)

        st.markdown(answer)

        if voice_mode:
            asyncio.run(speak_alpha(answer))

        st.session_state.messages.append({"role":"assistant","content":answer})
