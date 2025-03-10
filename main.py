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

# Convert to DataFrame
df = pd.DataFrame(rows.data)

# Display the DataFrame
st.write(df)

# Get the number of rows
num_rows = df.shape[0]

# Display the row count in Streamlit
st.write(f"Total number of rows: {num_rows}")