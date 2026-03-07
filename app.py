import streamlit as st
from groq import Groq
import sys
import time
from io import StringIO
from streamlit_mic_recorder import speech_to_text
import hashlib
import random
import datetime
import pandas as pd
import plotly.express as px
import requests
import urllib.parse
import json
import os
import base64
from PyPDF2 import PdfReader

# --- 1. Page Configuration ---
st.set_page_config(page_title="Alpha AI ⚡ Created by Hasith", page_icon="⚡", layout="wide")

# --- 2. Loading Screen (7 Seconds) ---
if "loaded" not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <style>
                .loader-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; }
                .alpha-text { font-size: 50px; font-weight: bold; color: #FFD700; text-shadow: 0 0 20px #FF8C00; margin-bottom: 20px; font-family: 'Arial Black', sans-serif; }
                .loading-bar { width: 300px; height: 4px; background: #333; border-radius: 2px; overflow: hidden; position: relative; }
                .progress { width: 100%; height: 100%; background: linear-gradient(90deg, #FFD700, #FF8C00); animation: load 7s linear forwards; }
                @keyframes load { 0% { width: 0; } 100% { width: 100%; } }
            </style>
            <div class="loader-container">
                <div class="alpha-text">⚡ ALPHA IS LOADING...</div>
                <div class="loading-bar"><div class="progress"></div></div>
                <p style="color: #888; margin-top: 15px;">Initializing Llama 4 Scout Vision by Hasith</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(7)
    st.session_state.loaded = True
    placeholder.empty()
    st.rerun()

# --- 3. Session State Initialization ---
if "user_db" not in st.session_state:
    st.session_state.user_db = {
        "matheesha": {"password": "123", "vault": [], "role": "VIP"},
        "sadev": {"password": "123", "vault": [], "role": "VIP"}
    }
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# --- 4. Custom UI Styling ---
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:25px; font-size: 20px; }
    .vault-card { background: #262626; border-left: 5px solid #FFD700; padding: 10px; border-radius: 5px; margin-bottom: 5px; font-size: 13px; }
    .warning-text { color: #ff4b4b; font-weight: bold; border: 1px solid #ff4b4b; padding: 10px; border-radius: 5px; text-align: center; background: rgba(255, 75, 75, 0.1); margin-bottom: 15px; }
    .bypass-text { color: #FFD700; font-weight: bold; font-size: 14px; text-align: center; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 5. Security Portal with Creator Bypass ---
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ Access Portal</h1>', unsafe_allow_html=True)
    
    # Adding the requested Bypass Tab
    tab_login, tab_reg, tab_bypass = st.tabs(["🔐 Login", "📝 Register", "⚡ Creator & His Friends Bypass"])
    
    with tab_login:
        username_in = st.text_input("Username").lower().strip()
        password_in = st.text_input("Password", type="password")
        
        admin_verified = False
        if username_in == "hasith123":
            st.markdown('<div class="warning-text">Enter Secret Name (හසිත් පහ)</div>', unsafe_allow_html=True)
            verify_name = st.text_input("Secret Verification", key="admin_login_verify")
            if verify_name == "හසිත් පහ":
                admin_verified = True
                
        if st.button("Access Alpha"):
            if username_in == "hasith123" and password_in == "hasith@alpha":
                if admin_verified:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username_in
                    st.rerun()
                else:
                    st.error("Verification Name is Incorrect!")
            elif username_in in st.session_state.user_db:
                stored_pass = st.session_state.user_db[username_in]["password"]
                if password_in == stored_pass or check_hashes(password_in, stored_pass):
                    st.session_state.logged_in = True
                    st.session_state.current_user = username_in
                    st.rerun()
                else:
                    st.error("Invalid Credentials.")

    with tab_reg:
        new_user = st.text_input("New Username", key="reg_u")
        new_pass = st.text_input("New Password", type="password", key="reg_p")
        if st.button("Create Account"):
            if new_user and new_user not in st.session_state.user_db:
                st.session_state.user_db[new_user] = {"password": make_hashes(new_pass), "vault": [], "role": "Guest"}
                st.success("Account Created!"); st.rerun()
                
    with tab_bypass:
        st.markdown('<div class="bypass-text">⚡ Creator Exclusive Unlock</div>', unsafe_allow_html=True)
        bypass_username = st.text_input("Enter Bypass Username", key="bypass_field").strip()
        
        if st.button("Unlock Alpha"):
            if bypass_username == "Hasith12378":
                st.session_state.logged_in = True
                st.session_state.current_user = "hasith123" # Login as Admin
                st.success("Creator Verified! Welcome Hasith.")
                st.rerun()
            else:
                st.error("Unauthorized Username! Only Hasith12378 is allowed.")
    st.stop()

# --- 6. Main App (Unchanged Logic) ---
current_user = st.session_state.current_user
with st.sidebar:
    if current_user == "hasith123":
        st.markdown(f"### 👑 Admin: {len(st.session_state.user_db)} Users")
    
    st.subheader("📄 Document Analyzer")
    doc_file = st.file_uploader("Upload PDF/TXT", type=["pdf", "txt"])
    extracted_text = ""
    if doc_file:
        if doc_file.type == "application/pdf":
            pdf_reader = PdfReader(doc_file)
            extracted_text = "".join([page.extract_text() for page in pdf_reader.pages])
        else:
            extracted_text = doc_file.getvalue().decode()

    st.write("---")
    ai_mode_selection = st.radio("Intelligence Level", ["Normal (Llama 3.3)", "Pro (GPT OSS 120B)", "Vision (Llama 4 Scout) 👁️"])
    chat_persona = st.selectbox("Persona", ["Standard Alpha", "Image Creator 🎨", "Data Analyst 📊"])
    enable_web_search = st.checkbox("🌐 Enable Web Search") if "Vision" not in ai_mode_selection else False

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Mode: {ai_mode_selection}</div>', unsafe_allow_html=True)

base64_img = None
if "Vision" in ai_mode_selection:
    vision_file = st.file_uploader("🖼️ Upload Image for Analysis", type=["jpg", "png", "jpeg"])
    if vision_file:
        st.image(vision_file, width=300)
        base64_img = base64.b64encode(vision_file.getvalue()).decode()

client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
user_query = st.chat_input("Ask Alpha...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"): st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Alpha is thinking..."):
            if "Vision" in ai_mode_selection:
                active_model = "llama-4-scout-17b-16e-instruct"
                v_content = [{"type": "text", "text": user_query}]
                if base64_img:
                    v_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}})
                chat_payload = [{"role": "user", "content": v_content}]
            else:
                active_model = "openai/gpt-oss-120b" if "Pro" in ai_mode_selection else "llama-3.3-70b-versatile"
                sys_inst = f"You are Alpha AI by Hasith. Document context: {extracted_text[:1000]}"
                chat_payload = [{"role": "system", "content": sys_inst}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]

            try:
                response = client_groq.chat.completions.create(model=active_model, messages=chat_payload)
                ans = response.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            except Exception as e:
                st.error(f"Error: {e}")
