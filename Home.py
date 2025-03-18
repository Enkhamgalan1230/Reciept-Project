import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time

#This is the main file, not rlly home page.

# Set page title and icon
st.set_page_config(
    page_title="Reciept",  # Set the title in the navigation bar
    page_icon="📃",  # Set a custom icon (optional)
    layout="wide"  # Optionally, set layout to 'wide' or 'centered'
)

# Page Setup

home_page = st.Page(
    page = "pages/1_home.py",
    title= "Home Page",
    icon = "🏠"
)

data_collection = st.Page(
    page = "pages/2_data_collection.py",
    title= "Data Collection",
    icon = "💾"
)

data = st.Page(
    page = "pages/3_data.py",
    title= "Data",
    icon = "📋"
)

price_comparison = st.Page(
    page = "pages/4_price_comparison.py",
    title= "Price Comparison",
    icon = "🆚"
)

page_5 = st.Page(
    page = "pages/5_fifth.py",
    title= "Fifth",
    icon = "❤️"
)

page_6 = st.Page(
    page = "pages/6_sixth.py",
    title= "Third",
    icon = "❤️"
)

pg = st.navigation(
    {
        "Info": [home_page],
        "Data":[data_collection,data],
        "Main Logics": [price_comparison,page_5,page_6]
        
    }
)
st.logo("assets/logo_longer.png",icon_image="assets/logo.png", size= "large")

pg.run()

