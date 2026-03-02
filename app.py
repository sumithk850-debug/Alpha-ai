import streamlit as st
from groq import Groq
import sqlite3
import bcrypt
import json
import numpy as np
from datetime import datetime

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Alpha AI ⚡", layout="wide")

# ==============================
# DATABASE SETUP
# ==============================
conn = sqlite3.connect("alpha_ai.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    plan TEXT DEFAULT 'free'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS memory(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    role TEXT,
    content TEXT,
    embedding TEXT,
    timestamp TEXT
)
""")

conn.commit()

# ==============================
# AUTH FUNCTIONS
# ==============================
def register(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users(username,password) VALUES(?,?)",
                       (username, hashed))
        conn.commit()
        return True
    except:
        return False

def login(username, password):
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    data = cursor.fetchone()
    if data:
        return bcrypt.checkpw(password.encode(), data[0])
    return False

def get_plan(username):
    cursor.execute("SELECT plan FROM users WHERE username=?", (username,))
    return cursor.fetchone()[0]

def upgrade_user(username):
    cursor.execute("UPDATE users SET plan='premium' WHERE username=?", (username,))
    conn.commit()

# ==============================
# VECTOR MEMORY
# ==============================
def create_embedding(text):
    return np.random.rand(384).tolist()

def save_memory(username, role, content):
    embedding = create_embedding(content)
    cursor.execute("INSERT INTO memory(username,role,content,embedding,timestamp) VALUES(?,?,?,?,?)",
                   (username, role, content, json.dumps(embedding), str(datetime.now())))
    conn.commit()

def load_memory(username):
    cursor.execute("SELECT role,content FROM memory WHERE username=? ORDER BY id ASC", (username,))
    return cursor.fetchall()

# ==============================
# SESSION
# ==============================
if "user" not in st.session_state:
    st.session_state.user = None

# ==============================
# LOGIN PAGE
# ==============================
if not st.session_state.user:
    st.title("🔐 Alpha AI Login")

    mode = st.radio("Select Option", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if mode == "Register":
        if st.button("Create Account"):
            if register(username, password):
                st.success("Account Created Successfully")
            else:
                st.error("Username Already Exists")

    if mode == "Login":
        if st.button("Login"):
            if login(username, password):
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid Credentials")

    st.stop()

# ==============================
# MAIN APP
# ==============================
st.sidebar.success(f"Logged in as {st.session_state.user}")
plan = get_plan(st.session_state.user)
st.sidebar.info(f"Plan: {plan}")

if st.sidebar.button("Upgrade to Premium 💳"):
    upgrade_user(st.session_state.user)
    st.sidebar.success("Upgraded to Premium!")
    st.rerun()

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

# ==============================
# ADMIN DASHBOARD
# ==============================
if st.session_state.user == "admin":
    st.sidebar.title("📊 Admin Panel")
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE plan='premium'")
    premium_users = cursor.fetchone()[0]

    st.sidebar.write(f"Total Users: {total_users}")
    st.sidebar.write(f"Premium Users: {premium_users}")

# ==============================
# AI ENGINE
# ==============================
st.title("Alpha AI ⚡")
st.caption("Created by Hasith")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    history = load_memory(st.session_state.user)
    st.session_state.messages = [
        {"role": role, "content": content}
        for role, content in history
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask Alpha AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_memory(st.session_state.user, "user", prompt)

    with st.chat_message("assistant"):
        model_name = "llama-3.3-70b-versatile" if plan == "premium" else "llama3-8b-8192"

        stream = client.chat.completions.create(
            model=model_name,
            messages=st.session_state.messages[-15:],
            stream=True
        )

        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})
    save_memory(st.session_state.user, "assistant", response)
