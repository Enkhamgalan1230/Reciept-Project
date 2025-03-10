import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase

st.title("Hello World 👋")
 
# Fetch Data from Supabase Table
def fetch_data():
    response = supabase.table("Product").select("*").execute()
    return response.data

# Display Data
if st.button("Fetch Data"):
    data = fetch_data()
    st.write(data)