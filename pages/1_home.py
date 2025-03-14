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

# Create layout columns
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    pass

# Add this after your text markdown to check text color and update icons
st.markdown(
    """
    <p id="theme-detect" style="color: var(--text-color); display: none;">Theme</p>
    <script>
        // Detect text color
        let textColor = window.getComputedStyle(document.getElementById("theme-detect")).color;
        let isDarkMode = textColor === "rgb(255, 255, 255)"; // White text means dark mode

        // Change icons dynamically
        document.documentElement.style.setProperty("--email-icon", isDarkMode ? "data:image/png;base64,{email_base64_white}" : "data:image/png;base64,{email_base64_black}");
        document.documentElement.style.setProperty("--github-icon", isDarkMode ? "data:image/png;base64,{github_base64_white}" : "data:image/png;base64,{github_base64_black}");
        document.documentElement.style.setProperty("--phone-icon", isDarkMode ? "data:image/png;base64,{phone_base64_white}" : "data:image/png;base64,{phone_base64_black}");
    </script>
    """,
    unsafe_allow_html=True
)

# Update the icon display using the new CSS variables
with col2:
    st.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; text-align: center; margin-top: 20px;">
            <a href="mailto:enkhamgalan.entwan@outlook.com" target="_blank" style="text-decoration: none;">
                <img src="var(--email-icon)" 
                    alt="Email" 
                    style="width: 40px; height: auto; cursor: pointer; transition: transform 0.2s ease-in-out;">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; text-align: center; margin-top: 20px;">
            <a href="https://github.com/Enkhamgalan1230/Reciept-Project" target="_blank" style="text-decoration: none;">
                <img src="var(--github-icon)" 
                    alt="GitHub" 
                    style="width: 45px; height: auto; cursor: pointer; transition: transform 0.2s ease-in-out;">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; text-align: center; margin-top: 20px;">
            <a href="tel:07310545410" style="text-decoration: none;">
                <img src="phone_base64_black" 
                    alt="Phone" 
                    style="width: 40px; height: auto; cursor: pointer; transition: transform 0.2s ease-in-out;">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

with col5:
    pass