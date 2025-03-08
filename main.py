import streamlit as st
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
from st_supabase_connection import SupabaseConnection

st.title("Hello World 👋")

# Initialize connection
conn = st.connection("supabase", type=SupabaseConnection)

# Perform query
rows = conn.query("*", table="mytable", ttl="10m").execute()

# Print results
if rows.data:
    for row in rows.data:
        st.write(f"{row['name']} has a :{row['pet']}:")
else:
    st.write("No data found!")
