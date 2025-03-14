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

# Function to convert image to Base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Convert image to Base64
email = "assets/email-white.png"  # Adjust this based on your file location
github = "assets/github-white.png"
phone = "assets/phone-white.png"

email_base64 = get_base64_image(email)
github_base64 = get_base64_image(github)
phone_base64 = get_base64_image(phone)



col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
            f"""
        <div style="display: flex; justify-content: center; align-items: center; text-align: right; margin-top: 20px;">
            <a href="mailto:enkhamgalan.entwan@outlook.com" target="_blank" style="text-decoration: none;">
                <img src="data:image/png;base64,{email_base64}" 
                    alt="Email" 
                    style="width: 50px; height: auto; cursor: pointer; transition: transform 0.2s ease-in-out;">
            </a>
        </div>
        <style>
            img:hover {{
                transform: scale(1.1);
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
            f"""
        <div style="display: flex; justify-content: center; align-items: center; text-align: center; margin-top: 20px;">
            <a href="mailto:enkhamgalan.entwan@outlook.com" target="_blank" style="text-decoration: none;">
                <img src="data:image/png;base64,{github_base64}" 
                    alt="github" 
                    style="width: 50px; height: auto; cursor: pointer; transition: transform 0.2s ease-in-out;">
            </a>
        </div>
        <style>
            img:hover {{
                transform: scale(1.1);
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
            f"""
        <div style="display: flex; justify-content: center; align-items: center; text-align: left; margin-top: 20px;">
            <a href="mailto:enkhamgalan.entwan@outlook.com" target="_blank" style="text-decoration: none;">
                <img src="data:image/png;base64,{phone_base64}" 
                    alt="github" 
                    style="width: 50px; height: auto; cursor: pointer; transition: transform 0.2s ease-in-out;">
            </a>
        </div>
        <style>
            img:hover {{
                transform: scale(1.1);
            }}
        </style>
        """,
        unsafe_allow_html=True
    )