import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time
import base64
import streamlit.components.v1 as components


# Set page title and icon
st.set_page_config(
    page_title="Receipt",  # Set the title in the navigation bar
    page_icon="📃",  # Set a custom icon (optional)
    layout="wide"  # Optionally, set layout to 'wide' or 'centered'
)
# Page Setup

# Inject a hidden HTML tag that stores the theme mode (optional)
st.markdown(
    """
    <script>
        const themeDiv = document.createElement('div');
        themeDiv.id = 'theme-detector';
        themeDiv.style.display = 'none';
        themeDiv.innerText = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        document.body.appendChild(themeDiv);
    </script>
    """,
    unsafe_allow_html=True
)

# Delay slightly to let JS take effect
time.sleep(0.1)

home_page = st.Page(
    page = "page_numbers/1_home.py",
    title= "Home Page",
    icon = "🏠"
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

data_fetcher = st.Page(
    page = "page_numbers/data_fetcher.py",
    title= "Data Fetcher",
    icon = "🛠️"
)


pg = st.navigation(
    {
        "Info": [home_page],
        "Data":[data_collection,data],
        "Main Logics": [price_comparison,price_inflation,price_prediction,store, receipt],
        "Boring Stuff": [data_fetcher]
    }
)


# ✅ Custom logo that switches with theme
st.markdown(
    """
    <style>
    .dark-logo { display: none; }
    @media (prefers-color-scheme: dark) {
        .light-logo { display: none !important; }
        .dark-logo { display: block !important; }
    }
    </style>
    
    <img src="assets/logo_longer_black.png" class="light-logo" style="width: 250px; margin-bottom: 1rem;" />
    <img src="assets/logo_longer_white.png" class="dark-logo" style="width: 250px; margin-bottom: 1rem;" />
    """,
    unsafe_allow_html=True
)

pg.run()

