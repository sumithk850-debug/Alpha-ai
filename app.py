import streamlit as st
from supabase import create_client, Client
import extra_streamlit_components as stx
from huggingface_hub import InferenceClient
from groq import Groq
import requests, base64, asyncio, json, datetime, random, urllib.parse
import edge_tts
from duckduckgo_search import DDGS

# -----------------------
# 1. API & Database Setup
# -----------------------
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Alpha AI | Ultimate", layout="wide", page_icon="⚡")

# -----------------------
# 2. Cookie & Session Management
# -----------------------
cookie_manager = stx.CookieManager()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = None
if "messages" not in st.session_state: st.session_state.messages = []
if "generated_image" not in st.session_state: st.session_state.generated_image = None

# Cookie එක පරීක්ෂා කර අවුරුද්දක් යනකම් ලොගින් එක තබා ගැනීම
saved_token = cookie_manager.get(cookie="alpha_master_token")
if saved_token and not st.session_state.logged_in:
    try:
        res = supabase.table("profiles").select("*").eq("master_key", saved_token).execute()
        if res.data:
            st.session_state.user_data = res.data[0]
            st.session_state.logged_in = True
    except: pass

# -----------------------
# 3. Helper Functions
# -----------------------
def generate_master_key():
    return f"ALPHA-{random.randint(100, 999)}-{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"

def check_user_access(email):
    # Developer (Hasith) හට සැමවිටම Unlimited
    if email == "hasith@mbsl.com": return True, 0, True # ඔබේ නිවැරදි ඊමේල් එක මෙතනට දාන්න
    
    today = str(datetime.date.today())
    try:
        res = supabase.table("profiles").select("*").eq("email", email).execute()
        if res.data:
            user = res.data[0]
            is_vip = user.get('is_pro', False)
            if is_vip: return True, 0, True
            
            # දිනය වෙනස් නම් Count එක Reset කිරීම
            if user.get('last_img_date') != today:
                supabase.table("profiles").update({"last_img_date": today, "img_count": 0}).eq("email", email).execute()
                return True, 0, False
            
            return (user['img_count'] < 5), user['img_count'], False
    except: return True, 0, False
    return False, 0, False

def update_usage(email, current_count):
    try:
        supabase.table("profiles").update({"img_count": current_count + 1}).eq("email", email).execute()
    except: pass

async def speak_alpha(text):
    try:
        comm = edge_tts.Communicate(text, "en-US-SteffanNeural")
        audio = b""
        async for chunk in comm.stream():
            if chunk["type"]=="audio": audio+=chunk["data"]
        if audio:
            b64 = base64.b64encode(audio).decode()
            st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# -----------------------
# 4. Auth UI (Name & Email Only)
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center; color:#FFD700;">⚡ ALPHA AI CORE</h1>', unsafe_allow_html=True)
    tab_log, tab_reg = st.tabs(["🔑 Sign In", "📝 Register"])

    with tab_reg:
        u_name = st.text_input("Full Name")
        u_email = st.text_input("Email Address")
        if st.button("Register"):
            if u_name and u_email:
                m_key = generate_master_key()
                try:
                    supabase.table("profiles").insert({
                        "full_name": u_name, "email": u_email, "master_key": m_key,
                        "is_pro": False, "img_count": 0, "last_img_date": str(datetime.date.today())
                    }).execute()
                    st.success(f"Success! Master Key: {m_key}")
                except: st.error("Email already exists.")

    with tab_log:
        l_email = st.text_input("Email", key="l_email")
        l_key = st.text_input("Master Key", type="password")
        if st.button("Login"):
            res = supabase.table("profiles").select("*").eq("email", l_email).eq("master_key", l_key).execute()
            if res.data:
                st.session_state.user_data = res.data[0]
                st.session_state.logged_in = True
                cookie_manager.set("alpha_master_token", l_key, expires_at=datetime.datetime.now() + datetime.timedelta(days=365))
                st.rerun()
            else: st.error("Invalid credentials.")
    st.stop()

# -----------------------
# 5. Dashboard UI
# -----------------------
u_info = st.session_state.user_data
can_gen, count, is_vip = check_user_access(u_info['email'])

st.markdown(f"""
<div style="background: linear-gradient(90deg, #FFD700, #FF8C00); padding:10px; border-radius:15px; text-align:center; color:black; font-weight:bold; display:flex; justify-content:space-between; align-items:center;">
    <span>⚡ ALPHA AI ULTIMATE</span>
    <button style="background:black; color:white; border:none; padding:5px 15px; border-radius:10px;">BUY FULL VERSION</button>
    <span>{'💎 PREMIUM' if is_vip else f'📸 Daily: {count}/5'} | {u_info['full_name']}</span>
</div>
""", unsafe_allow_html=True)

# -----------------------
# 6. Main Features (Tabs)
# -----------------------
tab_chat, tab_img = st.tabs(["💬 Chat", "🎨 Image Lab"])

with tab_img:
    img_p = st.text_input("Describe your vision:")
    img_model = st.selectbox("Model:", ["flux-schnell", "turbo", "zimage"])
    if st.button("Generate Photo"):
        if can_gen:
            with st.spinner("Painting..."):
                seed = random.randint(1, 1000000)
                url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(img_p)}?width=1024&height=1024&seed={seed}&model={img_model}&nologo=true"
                res = requests.get(url)
                if res.status_code == 200:
                    st.session_state.generated_image = res.content
                    if not is_vip: update_usage(u_info['email'], count)
                    st.rerun()
        else: st.error("Daily limit reached! Buy Full Version for unlimited access.")
    
    if st.session_state.generated_image:
        st.image(st.session_state.generated_image)

with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    u_input = st.chat_input("Command Alpha...")
    if u_input:
        st.session_state.messages.append({"role": "user", "content": u_input})
        with st.chat_message("user"): st.markdown(u_input)
        # AI Response logic (Groq/Llama) පරණ විදිහටම මෙතනට එයි...
