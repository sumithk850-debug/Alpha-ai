import streamlit as st
from github import Github
import os

# 1. GitHub සම්බන්ධතාවය ඇති කිරීම
# Streamlit Secrets වලින් හෝ Local .env එකකින් Token එක ලබා ගැනීම
def get_github_client():
    if "GITHUB_TOKEN" in st.secrets:
        token = st.secrets["GITHUB_TOKEN"]
    else:
        # Local එකේ වැඩ කරද්දී භාවිතා කිරීමට
        token = os.getenv("GITHUB_TOKEN")
        
    if not token:
        st.error("GitHub Token එක හමු වූයේ නැත! කරුණාකර Secrets පරීක්ෂා කරන්න.")
        return None
    return Github(token)

def create_github_repo(repo_name, files_dict):
    g = get_github_client()
    if g:
        try:
            user = g.get_user()
            # අලුත් Repository එකක් සෑදීම
            repo = user.create_repo(repo_name, auto_init=True)
            
            # ලිපිගොනු ඇතුළත් කිරීම
            for file_name, content in files_dict.items():
                repo.create_file(file_name, f"Alpha AI: Adding {file_name}", content)
            
            return repo.html_url
        except Exception as e:
            return f"Error: {str(e)}"
    return None

# --- UI කොටස ---
st.title("🤖 Alpha AI: GitHub Automator")
st.subheader("අලුත් ව්‍යාපෘතියක් GitHub වෙත යවන්න")

repo_name = st.text_input("ව්‍යාපෘතියේ නම (Project Name):", placeholder="e.g., my-new-app")
description = st.text_area("කෙටි විස්තරයක්:")

if st.button("GitHub වෙත යොමු කරන්න (Push to GitHub)"):
    if repo_name:
        with st.spinner("Alpha AI වැඩ කරමින් පවතී..."):
            # මෙහිදී AI එක මගින් නිපදවන ගොනු ලැයිස්තුව ඇතුළත් කරන්න
            # දැනට උදාහරණයක් ලෙස සරල ගොනු දෙකක්:
            example_files = {
                "main.py": f"# Project: {repo_name}\nprint('Hello World!')",
                "README.md": f"# {repo_name}\n{description}\n\nCreated by Alpha AI"
            }
            
            result_url = create_github_repo(repo_name, example_files)
            
            if "Error" in result_url:
                st.error(result_url)
            else:
                st.success(f"සාර්ථකයි! ඔබේ ව්‍යාපෘතිය මෙතැනින් බලන්න:")
                st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") # සරල සැමරුමක් ලෙස
                st.write(result_url)
    else:
        st.warning("කරුණාකර ව්‍යාපෘතියේ නම ඇතුළත් කරන්න.")
