import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time

# Set page title and icon
st.set_page_config(
    page_title="Reciept",  # Set the title in the navigation bar
    page_icon="📃",  # Set a custom icon (optional)
    layout="wide"  # Optionally, set layout to 'wide' or 'centered'
)

st.title("Welcome to Reciept 👋")


st.markdown("<br><br>", unsafe_allow_html=True)  # Adds vertical spacing

# Create two columns
col1, col2 = st.columns([1, 2])  # Adjust column ratio

# Left Column: Centered Image
with col1:
    st.markdown(
        """
        <div style="display: flex; justify-content: center;">
            <img src="page.png" width="180">
        </div>
        """,
        unsafe_allow_html=True,
    )

# Right Column: Vertically Centered Text
with col2:
    st.markdown(
        """
        <div style="display: flex; align-items: center; height: 100%; text-align: left;">
            <h3>What is Reciept 🤔?</h3>
            <p>Easily manage receipts, track your expenses, and compare prices across stores.</p>
            <p>Save money by making informed decisions. Start today! 🚀</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Divider
st.markdown("<br><br><hr>", unsafe_allow_html=True)  # Adds spacing and a divider
