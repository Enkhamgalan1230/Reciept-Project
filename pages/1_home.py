import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time

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
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        '<a href="mailto:enkhamgalan.entwan@outlook.com" target="_blank" style="text-decoration: none;">'
        '<button style="width:100%; padding: 10px; border-radius: 10px; border: none; background-color: #0073e6; color: white; font-size: 16px; cursor: pointer;">📧 Email</button>'
        '</a>',
        unsafe_allow_html=True  # Allows raw HTML rendering
    )

with col2:
    pass

with col3:
    pass