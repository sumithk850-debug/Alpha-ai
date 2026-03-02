import streamlit as st
from groq import Groq
import sqlite3
import numpy as np
import json
from datetime import datetime
import sys, io

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Alpha AI ⚡", layout="wide")

# ==============================
# DATABASE SETUP
# ==============================
conn = sqlite3.connect("alpha_ai.db", check_same_thread=False)
cursor = conn.cursor()

# Users table (for future multi-user)
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    plan TEXT DEFAULT 'premium'
)
""")

# Memory table
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
# AUTO USER (Owner Only)
# ==============================
if "user" not in st.session_state:
    st.session_state.user = "hasith"  # Owner only

username = st.session_state.user
plan = "premium"  # Owner always premium

# ==============================
# VECTOR MEMORY FUNCTIONS
# ==============================
def create_embedding(text):
    return np.random.rand(384).tolist()

def save_memory(role, content):
    try:
        # Ensure content is string
        if content is None:
            content_text = ""
        elif isinstance(content, str):
            content_text = content
        else:
            content_text = str(content)

        embedding = create_embedding(content_text)
        cursor.execute(
            "INSERT INTO memory(username,role,content,embedding,timestamp) VALUES(?,?,?,?,?)",
            (username, role, content_text, json.dumps(embedding), str(datetime.now()))
        )
        conn.commit()
    except Exception as e:
        st.error(f"Memory save failed: {e}")

def load_memory():
    cursor.execute(
        "SELECT role,content FROM memory WHERE username=? ORDER BY id ASC",
        (username,)
    )
    return cursor.fetchall()

# ==============================
# SESSION STATE
# ==============================
if "messages" not in st.session_state:
    history = load_memory()
    st.session_state.messages = [{"role": role, "content": content} for role, content in history]

# ==============================
# SIDEBAR
# ==============================
st.sidebar.success(f"Logged in as {username}")
st.sidebar.info(f"Plan: {plan}")

if st.sidebar.button("Clear Chat Memory"):
    cursor.execute("DELETE FROM memory WHERE username=?", (username,))
    conn.commit()
    st.session_state.messages = []
    st.rerun()

# ==============================
# HEADER
# ==============================
st.title("Alpha AI ⚡")
st.caption("Created by Hasith – Owner Mode Only")

# ==============================
# ADMIN DASHBOARD
# ==============================
st.sidebar.title("📊 Owner Dashboard")
cursor.execute("SELECT COUNT(*) FROM memory WHERE username=?", (username,))
total_messages = cursor.fetchone()[0]
st.sidebar.write(f"Total Messages: {total_messages}")

# ==============================
# AI ENGINE
# ==============================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("GROQ_API_KEY missing in Streamlit Secrets!")
    st.stop()

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask Alpha AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_memory("user", prompt)

    with st.chat_message("assistant"):
        # Streaming AI
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages[-15:],
                stream=True
            )
            response = st.write_stream(stream)
        except Exception as e:
            response = f"AI Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": str(response)})
    save_memory("assistant", response)

# ==============================
# QUICK PYTHON RUNNER
# ==============================
st.sidebar.subheader("🐍 Python Lab")
py_code = st.sidebar.text_area("Write Python code here", height=150)
if st.sidebar.button("Run Code"):
    buffer = io.StringIO()
    sys.stdout = buffer
    try:
        exec(py_code)
        st.sidebar.code(buffer.getvalue() if buffer.getvalue() else "Done.", language="text")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
    finally:
        sys.stdout = sys.__stdout__
