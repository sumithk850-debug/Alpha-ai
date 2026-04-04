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
hf_client = InferenceClient(token=HF_TOKEN)

st.set_page_config(page_title="Alpha AI | Ultimate Edition", layout="wide", page_icon="⚡")

# -----------------------
# 2. Cookie & Session Management (Persistence)
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
# 3. Helper Functions (Voice, Search, Limits)
# -----------------------
def generate_master_key():
    return f"ALPHA-{random.randint(100, 999)}-{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"

def check_user_access(email):
    if email == "hasith@alpha.com": return True, 0, True # Dev Access
    today = str(datetime.date.today())
    try:
        res = supabase.table("profiles").select("*").eq("email", email).execute()
        if res.data:
            user = res.data[0]
            if user.get('is_pro', False): return True, 0, True
            if user.get('last_img_date') != today:
                supabase.table("profiles").update({"last_img_date": today, "img_count": 0}).eq("email", email).execute()
                return True, 0, False
            return (user['img_count'] < 5), user['img_count'], False
    except: return True, 0, False
    return False, 0, False

def update_usage(email, current_count):
    try: supabase.table("profiles").update({"img_count": current_count + 1}).eq("email", email).execute()
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

def web_search_tool(query):
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            if results: return "\n".join([f"Source: {r['title']} - {r['body']}" for r in results])
    except: return ""
    return ""

# -----------------------
# 4. Auth UI (Login/Register)
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center; color:#FFD700;">⚡ ALPHA AI CORE ACCESS</h1>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Sign In", "📝 Register"])
    with t2:
        u_n = st.text_input("Full Name")
        u_e = st.text_input("Email")
        if st.button("Register"):
            if u_n and u_e:
                m_k = generate_master_key()
                try:
                    supabase.table("profiles").insert({"full_name": u_n, "email": u_e, "master_key": m_k, "is_pro": False, "img_count": 0, "last_img_date": str(datetime.date.today())}).execute()
                    st.success(f"Success! Your Key: {m_k}")
                except: st.error("Email already exists.")
    with t1:
        l_e = st.text_input("Email", key="l_e")
        l_k = st.text_input("Master Key", type="password")
        if st.button("Login"):
            res = supabase.table("profiles").select("*").eq("email", l_e).eq("master_key", l_k).execute()
            if res.data:
                st.session_state.user_data = res.data[0]
                st.session_state.logged_in = True
                cookie_manager.set("alpha_master_token", l_k, expires_at=datetime.datetime.now() + datetime.timedelta(days=365))
                st.rerun()
            else: st.error("Invalid Key.")
    st.stop()

# -----------------------
# 5. UI Layout & Sidebar
# -----------------------
u_info = st.session_state.user_data
can_gen, count, is_vip = check_user_access(u_info['email'])

st.markdown(f"""
<div style="background: linear-gradient(90deg, #FFD700, #FF8C00); padding:10px; border-radius:15px; text-align:center; color:black; font-weight:bold; display:flex; justify-content:space-between; align-items:center;">
    <span>⚡ ALPHA AI ULTIMATE</span>
    <button style="background:black; color:white; border:none; padding:5px 15px; border-radius:10px; font-weight:bold;">BUY FULL VERSION</button>
    <span>{'💎 PREMIUM' if is_vip else f'📸 Photos: {count}/5'} | {u_info['full_name']}</span>
</div>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("Alpha Control")
    mode = st.radio("Intelligence", ["Normal", "Pro (GPT-OSS 120B)", "Ultra"])
    web_search_on = st.checkbox("Web Search", value=False)
    voice_on = st.checkbox("Voice Output", value=True)
    if st.button("Log Out"):
        cookie_manager.delete("alpha_master_token")
        st.session_state.logged_in = False
        st.rerun()

# -----------------------
# 6. Main Tabs (All Features)
# -----------------------
tab_chat, tab_img, tab_knowledge = st.tabs(["💬 Chat Intelligence", "🎨 Multimedia Lab", "📚 Alpha Knowledge"])

with tab_img:
    st.subheader("Image Generation (Pollinations v3)")
    img_p = st.text_input("Describe your vision (Transformers, Godzilla, etc.):")
    img_model = st.selectbox("Model:", ["flux-schnell", "turbo", "zimage"])
    if st.button("Generate Photo"):
        if can_gen:
            with st.spinner("Alpha is painting..."):
                seed = random.randint(1, 1000000)
                url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(img_p)}"
                headers = {"p-pollen-width": "1024", "p-pollen-height": "1024", "p-pollen-seed": str(seed), "p-pollen-model": img_model, "p-pollen-nologo": "true"}
                if POLLINATIONS_KEY: headers["Authorization"] = f"Bearer {POLLINATIONS_KEY}"
                res = requests.get(url, headers=headers, timeout=60)
                if res.status_code == 200:
                    st.session_state.generated_image = res.content
                    if not is_vip: update_usage(u_info['email'], count)
                    st.rerun()
        else: st.error("Daily limit (5/5) reached! Buy Full Version for unlimited.")
    if st.session_state.generated_image: st.image(st.session_state.generated_image, use_container_width=True)

with tab_knowledge:
    st.subheader("Specialized Knowledge Bases")
    col1, col2 = st.columns(2)
    with col1:
        st.info("🤖 **Blender & 3D Lab**")
        st.write("Rigging, Animation, Dynamic Paint scripts.")
    with col2:
        st.info("🦖 **Cinematic Lore**")
        st.write("Transformers, Godzilla, Marvel, Arthur C. Clarke.")

with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    u_input = st.chat_input("State your command, Master...")
    if u_input:
        st.session_state.messages.append({"role": "user", "content": u_input})
        with st.chat_message("user"): st.markdown(u_input)
        with st.chat_message("assistant"):
            res_p = st.empty()
            s_context = web_search_tool(u_input) if web_search_on else ""
            sys_msg = f"Name: Alpha AI. Dev: Hasith. Role: Expert in Blender, Transformers, Banking. Context: {s_context}"
            try:
                m_name = "llama-3.3-70b-versatile" if "Normal" in mode else "openai/gpt-oss-120b"
                stream = groq_client.chat.completions.create(model=m_name, messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:], stream=True)
                full_res = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        res_p.markdown(full_res + "▌")
                res_p.markdown(full_res)
                if voice_on: asyncio.run(speak_alpha(full_res))
                st.session_state.messages.append({"role": "assistant", "content": full_res})
            except Exception as e: st.error(f"Error: {e}")

st.divider()
st.caption("Alpha AI Ultimate | Created by Hasith")
