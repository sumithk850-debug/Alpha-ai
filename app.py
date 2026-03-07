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
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. Page Configuration ---
st.set_page_config(page_title="Alpha AI ⚡ Created by Hasith", page_icon="⚡", layout="wide")

# --- 2. Initialize Firebase (Cloud Storage) ---
if not firebase_admin._apps:
    try:
        if "FIREBASE_TYPE" in st.secrets:
            cred_dict = {
                "type": st.secrets["FIREBASE_TYPE"],
                "project_id": st.secrets["FIREBASE_PROJECT_ID"],
                "private_key_id": st.secrets["FIREBASE_PRIVATE_KEY_ID"],
                "private_key": st.secrets["FIREBASE_PRIVATE_KEY"].replace('\\n', '\n'),
                "client_email": st.secrets["FIREBASE_CLIENT_EMAIL"],
                "client_id": st.secrets["FIREBASE_CLIENT_ID"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{st.secrets['FIREBASE_CLIENT_EMAIL'].replace('@', '%40')}"
            }
            cred = credentials.Certificate(cred_dict)
        else:
            cred = credentials.Certificate('firebase_cred.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase Sync Error: {e}")

db = firestore.client()

# --- 3. Loading Screen (7 Seconds) ---
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

# --- 4. Database Helpers ---
def sync_db():
    users_ref = db.collection('users').stream()
    return {doc.id: doc.to_dict() for doc in users_ref}

if "user_db" not in st.session_state:
    st.session_state.user_db = sync_db()
    if not st.session_state.user_db:
        initial = {
            "matheesha": {"password": "123", "vault": [], "role": "VIP"},
            "sadev": {"password": "123", "vault": [], "role": "VIP"}
        }
        for k, v in initial.items():
            db.collection('users').document(k).set(v)
        st.session_state.user_db = initial

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# --- 5. Custom UI Styling ---
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:25px; font-size: 20px; }
    .vault-card { background: #262626; border-left: 5px solid #FFD700; padding: 10px; border-radius: 5px; margin-bottom: 5px; font-size: 13px; }
    .warning-text { color: #ff4b4b; font-weight: bold; border: 1px solid #ff4b4b; padding: 10px; border-radius: 5px; text-align: center; background: rgba(255, 75, 75, 0.1); margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 6. Security Portal ---
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ VIP Access Portal</h1>', unsafe_allow_html=True)
    tab_login, tab_reg = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab_login:
        username_in = st.text_input("Username").lower().strip()
        password_in = st.text_input("Password", type="password")
        
        admin_verified = False
        if username_in == "hasith123":
            st.markdown('<div class="warning-text">Enter Secret Name (හසිත් පහ)</div>', unsafe_allow_html=True)
            verify_name = st.text_input("Secret Verification", key="admin_verify_field")
            if verify_name == "හසිත් පහ":
                admin_verified = True
                
        if st.button("Access Alpha AI"):
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
            else:
                st.error("Account Not Found.")

    with tab_reg:
        new_user = st.text_input("New Username", key="reg_u_field")
        new_pass = st.text_input("New Password", type="password", key="reg_p_field")
        if st.button("Create Account"):
            if new_user and new_user not in st.session_state.user_db:
                user_data = {"password": make_hashes(new_pass), "vault": [], "role": "Guest"}
                db.collection('users').document(new_user).set(user_data)
                st.session_state.user_db = sync_db()
                st.success("Registration Successful!")
                st.rerun()
            else:
                st.error("Username already exists or invalid.")
    st.stop()

# --- 7. Sidebar & Features ---
current_user = st.session_state.current_user
with st.sidebar:
    if current_user == "hasith123":
        st.markdown(f"### 👑 Admin Panel: {len(st.session_state.user_db)} Users")
        st.caption(", ".join(st.session_state.user_db.keys()))
    
    st.subheader("📄 Document Analyzer")
    doc_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
    extracted_text = ""
    if doc_file:
        if doc_file.type == "application/pdf":
            pdf_reader = PdfReader(doc_file)
            extracted_text = "".join([page.extract_text() for page in pdf_reader.pages])
        else:
            extracted_text = doc_file.getvalue().decode()
        st.success("Document processed!")

    st.write("---")
    ai_mode_selection = st.radio("Intelligence Level", ["Normal (Llama 3.3)", "Pro (GPT OSS 120B)", "Vision (Llama 4 Scout) 👁️"])
    chat_persona = st.selectbox("Persona", ["Standard Alpha", "Image Creator 🎨", "Data Analyst 📊"])
    
    enable_web_search = st.checkbox("🌐 Enable Web Search") if "Vision" not in ai_mode_selection else False

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- 8. Main Interface ---
st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Mode: {ai_mode_selection}</div>', unsafe_allow_html=True)

# Vision Uploader
base64_img = None
if "Vision" in ai_mode_selection:
    vision_file = st.file_uploader("🖼️ Upload Image for Llama 4 Scout Analysis", type=["jpg", "png", "jpeg"])
    if vision_file:
        st.image(vision_file, width=300)
        base64_img = base64.b64encode(vision_file.getvalue()).decode()

# Chat logic
client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
user_query = st.chat_input("Ask Alpha...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Alpha is generating response..."):
            if "Vision" in ai_mode_selection:
                # Meta-llama/llama-4-scout-17b-16e-instruct
                active_model = "llama-4-scout-17b-16e-instruct"
                vision_content = [{"type": "text", "text": user_query}]
                if base64_img:
                    vision_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}})
                chat_payload = [{"role": "user", "content": vision_content}]
            else:
                active_model = "openai/gpt-oss-120b" if "Pro" in ai_mode_selection else "llama-3.3-70b-versatile"
                sys_instruction = f"You are Alpha AI created by Hasith. Document context: {extracted_text[:1000]}"
                chat_payload = [{"role": "system", "content": sys_instruction}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]

            try:
                response = client_groq.chat.completions.create(
                    model=active_model,
                    messages=chat_payload
                )
                res_text = response.choices[0].message.content
                st.markdown(res_text)
                st.session_state.messages.append({"role": "assistant", "content": res_text})
            except Exception as e:
                st.error(f"Error: {e}")
             
