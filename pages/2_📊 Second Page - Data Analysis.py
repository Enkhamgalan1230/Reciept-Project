import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time
from data_fetcher import fetch_data_with_progress  # Import the function

st.title("📊 Second Page - Data Analysis")

# Only show the progress bar the first time data is fetched
if "df" not in st.session_state:
    df = fetch_data_with_progress()  # This shows progress
    st.session_state.df = df  # Store in session state
else:
    df = st.session_state.df  # Load from session state (no progress bar)

if df is not None:
    st.write("🔍 Data Preview:")
    st.dataframe(df.head())  # Show data
else:
    st.write("⚠️ No data available.")
    