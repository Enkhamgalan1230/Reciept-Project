import streamlit as st
import pandas as pd
import time
import base64
import os
import re
from local_data import load_product_data
#os.environ["TRANSFORMERS_NO_TF"] = "1"

# Set page title and icon
st.set_page_config(
    page_title="Receipt",  # Set the title in the navigation bar
    page_icon="📃",  # Set a custom icon (optional)
    layout="wide"  # Optionally, set layout to 'wide' or 'centered'
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --receipt-ink:#f5f7f6; --receipt-muted:#b7c0ba; --receipt-green:#79c99a; --receipt-border:#303833; color-scheme:dark; }
html, body, [class*="css"] { font-family:'DM Sans', sans-serif; color:var(--receipt-ink); }
h1,h2,h3,h4,h5,h6 { font-family:'Space Grotesk', sans-serif !important; letter-spacing:-.025em; color:#ffffff !important; }
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child { background:#242825 !important; border-right:1px solid #353b37; }
[data-testid="stSidebarNav"] li a { border-radius:10px; margin:3px 8px; padding:9px 12px; font-weight:600; color:#ffffff !important; transition:background .15s ease,color .15s ease; }
[data-testid="stSidebarNav"] li a span, [data-testid="stSidebarNav"] li a p { color:#ffffff !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label { color:#ffffff !important; }
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"],
[data-testid="stAppViewContainer"] [data-testid="stText"] { color:#f5f7f6 !important; }
[data-testid="stMetric"] label,
[data-testid="stMetric"] [data-testid="stMetricValue"] { color:#ffffff !important; }
[data-testid="stMetric"] { background:#0e1117 !important; border-color:#303833; box-shadow:none; }
[data-testid="stDataFrame"] { color:#f5f7f6 !important; }
[data-testid="stSidebarNav"] li a:hover { background:#343a36 !important; color:#ffffff !important; }
[data-testid="stSidebarNav"] li a[aria-current="page"] { background:#414943 !important; color:#ffffff !important; box-shadow:0 3px 10px rgba(0,0,0,.2); }
[data-testid="stSidebarNav"] li a[aria-current="page"] span, [data-testid="stSidebarNav"] li a[aria-current="page"] p { color:#ffffff !important; }
[data-testid="stSidebarNav"] span { font-size:.9rem; }
.block-container { max-width:1400px; padding-top:2.5rem; padding-bottom:4rem; }
[data-testid="stMetric"] { border:1px solid var(--receipt-border); border-radius:14px; padding:1rem 1.1rem; }
.stButton>button,.stDownloadButton>button { border-radius:9px; font-weight:600; transition:transform .15s ease,box-shadow .15s ease; }
.stButton>button:hover,.stDownloadButton>button:hover { transform:translateY(-1px); box-shadow:0 5px 14px rgba(47,107,79,.16); }
[data-testid="stExpander"] { background:#0e1117; border-color:var(--receipt-border); border-radius:12px; }
hr { border-color:var(--receipt-border); }
</style>
""", unsafe_allow_html=True)
if "df" not in st.session_state:
    st.session_state.df = load_product_data()
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
 
update_password = st.Page(
     page = "page_numbers/update_password.py",
     title= "Forgot password"
)



pg = st.navigation(
    {
        "Info": [home_page],
        "Account": [login,mylist],
        "Insights": [data_collection,data],
        "Explore": [price_comparison,price_inflation,price_prediction,store, receipt],
        "Help": [helper, update_password],
    }
)

# Choose correct logo based on theme

logo_path = "assets/logo_longer_white.png"

# ✅ No base64 needed here
st.logo(image="assets/logo_longer_white.png", icon_image="assets/logo.png", size="large")

pg.run()

