import streamlit as st
from supabase import create_client, Client
import extra_streamlit_components as stx
from huggingface_hub import InferenceClient
from groq import Groq
import requests, base64, asyncio, json, datetime, random, urllib.parse
import edge_tts
from duckduckgo_search import DDGS

# -----------------------
# 1. API & Database Setup (Secrets)
# -----------------------
# මෙම විස්තර ඔබේ Streamlit Secrets වල නිවැරදිව තිබිය යුතුය.
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")
# Pollinations v3 සඳහා අවම වශයෙන් pollen 1ක් ඇති Token එකක් අවශ්‍යයි.
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY") 

groq_client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Alpha AI | Ultimate", layout="wide", page_icon="⚡")

# -----------------------
# 2. Cookie & Session Management (Persistence)
# -----------------------
cookie_manager = stx.CookieManager()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = None
if "messages" not in st.session_state: st.session_state.messages = []
if "generated_image" not in st.session_state: st.session_state.generated_image = None

# Cookie එක පරීක්ෂා කර අවුරුද්දක් යනකම් ලොගින් එක තබා ගැනීම (Auto-Login)
saved_token = cookie_manager.get(cookie="alpha_master_token")
if saved_token and not st.session_state.logged_in:
    try:
        res = supabase.table("profiles").select("*").eq("master_key", saved_token).execute()
        if res.data:
            st.session_state.user_data = res.data[0]
            st.session_state.logged_in = True
    except Exception: pass

# -----------------------
# 3. Helper Functions
# -----------------------
def generate_master_key():
    # රහස් කේතය නිර්මාණය කිරීම (උදා: ALPHA-784-X)
    return f"ALPHA-{random.randint(100, 999)}-{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"

def check_user_access(email):
    # Developer (Hasith) හට සැමවිටම Unlimited
    if email == "hasith@alpha.com": return True, 0, True # ඔබේ නිවැරදි ඊමේල් එක මෙතනට දාන්න
    
    today = str(datetime.date.today())
    try:
        res = supabase.table("profiles").select("*").eq("email", email).execute()
        if res.data:
            user = res.data[0]
            is_vip = user.get('is_pro', False)
            if is_vip: return True, 0, True
            
            # දවසකට පින්තූර 5 සීමාව පරීක්ෂා කිරීම
            if user.get('last_img_date') != today:
                # දවස වෙනස් නම් Count එක Reset කිරීම
                supabase.table("profiles").update({"last_img_date": today, "img_count": 0}).eq("email", email).execute()
                return True, 0, False
            
            return (user['img_count'] < 5), user['img_count'], False
    except Exception: return True, 0, False # Error එකක් ආවොත් Access දෙනවා
    return False, 0, False

def update_usage(email, current_count):
    # පින්තූරයක් හැදූ පසු Count එක වැඩි කිරීම
    try:
        supabase.table("profiles").update({"img_count": current_count + 1}).eq("email", email).execute()
    except Exception: pass

async def speak_alpha(text):
    # Alpha ගේ කටහඬ (TTS)
    try:
        comm = edge_tts.Communicate(text, "en-US-SteffanNeural")
        audio = b""
        async for chunk in comm.stream():
            if chunk["type"]=="audio": audio+=chunk["data"]
        if audio:
            b64 = base64.b64encode(audio).decode()
            st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except Exception: pass

def web_search_tool(query):
    # Web Search පද්ධතිය
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            if results: return "\n".join([f"Source: {r['title']} - {r['body']}" for r in results])
    except Exception: return ""
    return ""

# -----------------------
# 4. Auth UI (Login / Register)
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center; color:#FFD700;">⚡ ALPHA AI CORE</h1>', unsafe_allow_html=True)
    tab_log, tab_reg = st.tabs(["🔑 Sign In", "📝 Register"])

    with tab_reg:
        u_name = st.text_input("Full Name (ඔබේ නම)")
        u_email = st.text_input("Email Address (ඊමේල්)")
        if st.button("Register & Get Master Key"):
            if u_name and u_email:
                m_key = generate_master_key()
                try:
                    # Supabase Database එකට ඇතුළත් කිරීම
                    data = {
                        "full_name": u_name, "email": u_email, "master_key": m_key,
                        "is_pro": False, "img_count": 0, "last_img_date": str(datetime.date.today())
                    }
                    supabase.table("profiles").insert(data).execute()
                    st.success(f"Success! Welcome, {u_name}.")
                    st.code(f"YOUR MASTER KEY: {m_key}", language="text")
                    st.warning("⚠️ Copy and save this Key. You need it to login next time!")
                except Exception: st.error("Email already exists. Please use a different one.")
            else: st.info("Please fill all details.")

    with tab_log:
        l_email = st.text_input("Email", key="l_email")
        l_key = st.text_input("Master Key", type="password")
        if st.button("Login to Alpha"):
            res = supabase.table("profiles").select("*").eq("email", l_email).eq("master_key", l_key).execute()
            if res.data:
                st.session_state.user_data = res.data[0]
                st.session_state.logged_in = True
                # Cookie එක අවුරුද්දකට (දින 365) සේව් කිරීම
                cookie_manager.set("alpha_master_token", l_key, expires_at=datetime.datetime.now() + datetime.timedelta(days=365))
                st.rerun()
            else: st.error("Invalid credentials. Please check your Email and Master Key.")
    st.stop()

# -----------------------
# 5. Dashboard UI & Header
# -----------------------
u_info = st.session_state.user_data
can_gen, count, is_vip = check_user_access(u_info['email'])

# ඉහළින් පෙනෙන ලස්සන Header එක (BUY FULL VERSION බොත්තම සමඟ)
st.markdown(f"""
<div style="background: linear-gradient(90deg, #FFD700, #FF8C00); padding:10px; border-radius:15px; text-align:center; color:black; font-weight:bold; display:flex; justify-content:space-between; align-items:center;">
    <span>⚡ ALPHA AI ULTIMATE</span>
    <button style="background:black; color:white; border:none; padding:5px 15px; border-radius:10px; font-weight:bold; cursor:pointer;">BUY FULL VERSION</button>
    <span>{'💎 PREMIUM' if is_vip else f'📸 Daily Photos: {count}/5'} | {u_info['full_name']}</span>
</div>
""", unsafe_allow_html=True)

# -----------------------
# 6. Content Tabs
# -----------------------
tab_chat, tab_img = st.tabs(["💬 Chat Intelligence", "🎨 Image Generation Lab"])

with tab_img:
    st.subheader("Generate Image with Pollinations v3")
    img_p = st.text_input("Describe your vision:")
    # ඔයා එවපු ලිස්ට් එකේ තියෙන ලාභම models (1 pollen) මෙතනට දැම්මා.
    img_model = st.selectbox("Model:", ["flux-schnell", "turbo", "zimage"], index=0)
    if st.button("Generate Photo"):
        if can_gen:
            with st.spinner("Alpha is painting... 🖌️"):
                seed = random.randint(1, 1000000)
                url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(img_p)}"
                
                # Pollinations v3 සඳහා නිවැරදි headers (FIXED)
                # මෙම headers එකතු නොකළහොත් Image එක generate වෙන්නේ නැත.
                headers = {
                    "p-pollen-width": "1024",
                    "p-pollen-height": "1024",
                    "p-pollen-seed": str(seed),
                    "p-pollen-model": img_model,
                    "p-pollen-nologo": "true"
                }
                
                if POLLINATIONS_KEY:
                    # Token එක තිබේ නම් Authorization header එක එකතු කිරීම
                    headers["Authorization"] = f"Bearer {POLLINATIONS_KEY}"
                
                try:
                    res = requests.get(url, headers=headers, timeout=60)
                    if res.status_code == 200:
                        st.session_state.generated_image = res.content
                        if not is_vip: update_usage(u_info['email'], count)
                        st.rerun()
                    elif res.status_code == 402:
                        st.error("⚠️ Pollen Balance Low! Please check your Pollinations account.")
                    else: st.error(f"Error: {res.status_code}")
                except Exception as e: st.error(f"Error: {e}")
        else:
            st.error("ඔබේ දෛනික පින්තූර 5 සීමාව අවසන් වී ඇත. කරුණාකර හෙට උත්සාහ කරන්න හෝ Full Version එක ලබාගන්න.")
    
    if st.session_state.generated_image:
        st.image(st.session_state.generated_image, caption="Generated by Alpha AI", use_container_width=True)

with tab_chat:
    # Chat Logic (Groq/Llama) පරණ විදිහටම මෙතන ක්‍රියාත්මක වේ...
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    u_input = st.chat_input("State your command, Master...")
    if u_input:
        st.session_state.messages.append({"role": "user", "content": u_input})
        with st.chat_message("user"): st.markdown(u_input)
        
        with st.chat_message("assistant"):
            res_placeholder = st.empty()
            search_context = web_search_tool(u_input) if web_search_on else ""
            sys_msg = f"Your name is Alpha AI. Developed by Hasith. Context: {search_context}"
            try:
                stream = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:],
                    stream=True
                )
                full_res = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        res_placeholder.markdown(full_res + "▌")
                res_placeholder.markdown(full_res)
                if voice_on: asyncio.run(speak_alpha(full_res))
                st.session_state.messages.append({"role": "assistant", "content": full_res})
            except Exception as e: st.error(f"Error: {e}")

st.divider()
st.caption("Alpha AI Ultimate Edition | Powering the Future | Created by Hasith")
