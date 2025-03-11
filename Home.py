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

# Page Setup

home_page = st.Page(
    page = "pages/1_home.py",
    title= "Home Page",
    icon = "🏠"
)

data = st.Page(
    page = "pages/2_data_overview.py",
    title= "Data",
    icon = "📈"
)

page_3 = st.Page(
    page = "pages/3_third.py",
    title= "Third",
    icon = "❤️"
)

page_4 = st.Page(
    page = "pages/4_fourth.py",
    title= "Fourth",
    icon = "❤️"
)

page_5 = st.Page(
    page = "pages/5_fifth.py",
    title= "Fifth",
    icon = "❤️"
)

pg = st.navigation(
    {
        "Info": [home_page],
        "Project":[data, page_3,page_4,page_5]
    }
)
st.logo("assets/logo.png")
st.sidebar.text("Made by Entwan Enkhbayar")

pg.run()