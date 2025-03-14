import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time
import base64

st.title("Welcome to Reciept 👋")

st.markdown("---")

# Create two columns
col1, col2 = st.columns([1, 2], vertical_alignment="center", gap= "small")  # Adjust column ratio (1:2 for better alignment)

# Left Column: Image
with col1:
    st.image("assets/logo.png") 
    
# Right Column: Text
with col2:
    st.markdown(
        """
        #### What is Reciept 🤔?

        On tight budget this week?
        
        By analysing grocery prices across five different supermarkets, predicting and alerting users to potential price changes, 
        providing weekly price inflation status updates, and generating a personalised shopping list, 
        this app will help users manage their spending and make well-informed decisions 🚀.
        """
    )

# Divider
st.markdown("---")
# Create three columns


# Function to get base64 encoded image
def get_base64_image(image_path):
    import base64
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Load both light and dark mode images
email_base64_white = get_base64_image('assets/email-white.png')
github_base64_white = get_base64_image('assets/github-white.png')
phone_base64_white = get_base64_image('assets/phone-white.png')

email_base64_black = get_base64_image('assets/email-black.png')
github_base64_black = get_base64_image('assets/github-black.png')
phone_base64_black = get_base64_image('assets/phone-black.png')

# Function to detect theme color and return boolean
def is_dark_mode():
    st.markdown(
        """
        <p id="theme-detect" style="color: var(--text-color); display: none;">Theme</p>
        <script>
            let textColor = window.getComputedStyle(document.getElementById("theme-detect")).color;
            let isDarkMode = textColor === "rgb(255, 255, 255)"; // White text means dark mode
            sessionStorage.setItem("dark_mode", isDarkMode);
        </script>
        """,
        unsafe_allow_html=True
    )
    
    # JavaScript updates sessionStorage, but we can't get it directly in Python.
    # Assume default to light mode (False), as Streamlit can't read JS variables directly.
    return False  # This is a placeholder; JS updates sessionStorage dynamically

# Detect theme mode
dark_mode = is_dark_mode()

# Select icons based on theme
if dark_mode:
    email_base64 = email_base64_white
    github_base64 = github_base64_white
    phone_base64 = phone_base64_white
else:
    email_base64 = email_base64_black
    github_base64 = github_base64_black
    phone_base64 = phone_base64_black


# Create layout columns
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    pass

with col2:
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; text-align: center; margin-top: 20px;">
            <a href="mailto:enkhamgalan.entwan@outlook.com" target="_blank" style="text-decoration: none;">
                <img src="data:image/png;base64,{email_base64}" 
                    alt="Email" 
                    style="width: 40px; height: auto; cursor: pointer; transition: transform 0.2s ease-in-out;">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; text-align: center; margin-top: 20px;">
            <a href="https://github.com/Enkhamgalan1230/Reciept-Project" target="_blank" style="text-decoration: none;">
                <img src="data:image/png;base64,{github_base64}" 
                    alt="GitHub" 
                    style="width: 45px; height: auto; cursor: pointer; transition: transform 0.2s ease-in-out;">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; text-align: center; margin-top: 20px;">
            <a href="tel:07310545410" style="text-decoration: none;">
                <img src="data:image/png;base64,{phone_base64}" 
                    alt="Phone" 
                    style="width: 40px; height: auto; cursor: pointer; transition: transform 0.2s ease-in-out;">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

with col5:
    pass