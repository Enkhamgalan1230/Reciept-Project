import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase


# Define batch size (e.g., 10,000 rows at a time)
batch_size = 5000
offset = 0
all_rows = []


st.title("Hello World 👋")
 
# Fetch Data from Supabase Table
# Initialize connection.
conn = st.connection("supabase",type=SupabaseConnection)

while True:
    # Fetch batch of data
    rows = conn.table("Product").select("*").range(offset, offset + batch_size - 1).execute()

    # If no more data, stop loop
    if not rows.data:
        break

    # Append batch to list
    all_rows.extend(rows.data)

    # Increment offset for next batch
    offset += batch_size

# Convert list to DataFrame
df = pd.DataFrame(all_rows)


# Display total rows
st.write(f"Total number of rows fetched: {df.shape[0]}")

st.write(df.head(10))
st.write(df.tail(100))