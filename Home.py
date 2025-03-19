import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time
import base64

#This is the main file, not rlly home page.
# Function to convert image to Base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo = "assets/logo_longer_white.png"

email_base64 = get_base64_image(logo)
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
    icon = "📉"
)

data = st.Page(
    page = "pages/3_data_analysis.py",
    title= "Data Analysis",
    icon = "📈"
)

price_comparison = st.Page(
    page = "pages/4_price_comparison.py",
    title= "Price Comparison",
    icon = "🏷️"
)

price_inflation = st.Page(
    page = "pages/5_price_inflation.py",
    title= "Price Inflation",
    icon = "💷"
)

price_prediction = st.Page(
    page = "pages/6_price_prediction.py",
    title= "Price Prediction",
    icon = "🔮"
)

reciept = st.Page(
    page = "pages/7_reciept.py",
    title= "Reciept",
    icon = "📃"
)

data_fetcher = st.Page(
    page = "pages/data_fetcher.py",
    title= "Data Fetcher",
    icon = "🛠️"
)


pg = st.navigation(
    {
        "Info": [home_page],
        "Data":[data_collection,data],
        "Main Logics": [price_comparison,price_inflation,price_prediction, reciept],
        "Boring Stuff": [data_fetcher]
    }
)



st.logo("assets/logo_longer_white.png",icon_image="assets/logo.png", size= "large")

pg.run()

