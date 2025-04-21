import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time
import base64
import os
#os.environ["TRANSFORMERS_NO_TF"] = "1"

# Set page title and icon
st.set_page_config(
    page_title="Receipt",  # Set the title in the navigation bar
    page_icon="📃",  # Set a custom icon (optional)
    layout="wide"  # Optionally, set layout to 'wide' or 'centered'
)
# Page Setup

home_page = st.Page(
     page = "page_numbers/1_home.py",
     title= "Home Page",
     icon = "🏠"
 )
 
login = st.Page(
     page = "page_numbers/login.py",
     title = "Log in",
     icon = "👤"
 )
mylist = st.Page(
     page = "page_numbers/mylist.py",
     title = "My List",
     icon = "👤"
 )
 
data_collection = st.Page(
     page = "page_numbers/2_data_collection.py",
     title= "Data Collection",
     icon = "📉"
 )
 
data = st.Page(
     page = "page_numbers/3_data_analysis.py",
     title= "Data Analysis",
     icon = "📈"
 )
 
price_comparison = st.Page(
     page = "page_numbers/4_price_comparison.py",
     title= "Price Comparison",
     icon = "🏷️"
 )
 
price_inflation = st.Page(
     page = "page_numbers/5_price_inflation.py",
     title= "Price Inflation",
     icon = "💷"
 )
 
price_prediction = st.Page(
     page = "page_numbers/6_price_prediction.py",
     title= "Price Prediction",
     icon = "🔮"
 )
store = st.Page(
     page = "page_numbers/7_store.py",
     title= "Store Finder",
     icon = "📍"
 )
 
receipt = st.Page(
     page = "page_numbers/8_receipt.py",
     title= "Receipt",
     icon = "📃"
 )
 
helper = st.Page(
     page = "page_numbers/helper.py",
     title= "Helper",
 )
 
data_fetcher = st.Page(
     page = "page_numbers/data_fetcher.py",
     title= "Data Fetcher",
     icon = "🛠️"
 )




pg = st.navigation(
    {
        "Info": [home_page],
        "User ": [login,mylist],
        "Data ":[data_collection,data],
        "Main Logics ": [price_comparison,price_inflation,price_prediction,store, receipt],
        "Help": [helper],
        "Boring Stuff ": [data_fetcher]
    }
)

# Choose correct logo based on theme

logo_path = "assets/logo_longer_white.png"

# ✅ No base64 needed here
st.logo(image=logo_path, icon_image="assets/logo.png", size="large")

pg.run()

