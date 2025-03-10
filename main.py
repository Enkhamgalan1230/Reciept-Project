import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time

st.title("Hello World 👋")
 
# Initialize Supabase connection
conn = st.connection("supabase", type=SupabaseConnection)

# Initialize Supabase connection
conn = st.connection("supabase", type=SupabaseConnection)

# Step 1: Fetch full dataset using query caching (avoids pagination limits)
try:
    rows = conn.query("*", table="mytable", ttl="10m").execute()  # Caches result for 10 minutes
    df = pd.DataFrame(rows)  # Convert to DataFrame
    st.write(f"Total rows fetched: {df.shape[0]}")  # Display row count
except Exception as e:
    st.write(f"Error fetching data: {e}")
