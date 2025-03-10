import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase

st.title("Hello World 👋")
 
# Fetch Data from Supabase Table
# Initialize connection.
conn = st.connection("supabase",type=SupabaseConnection)

# Perform query.
rows = conn.table("Product").select("*").execute()

# Print results.
for row in rows.data:
    st.write(f"{row['Name']} has a :{row['Price']}:")

