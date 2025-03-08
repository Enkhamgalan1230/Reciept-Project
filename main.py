import streamlit as st
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine

st.title("Hello World 👋")

# Supabase credentials (Supavisor)
DB_USER = "postgres"
DB_PASSWORD = "lkjH0987@"
DB_HOST = "db.rgfhrhvdspwlexlymdga.supabase.co"
DB_NAME = "postgres"
SUPAVISOR_PORT = "6543"  # Supavisor uses port 6543 instead of 5432

DATABASE_URL = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

try:
    # Create database engine
    engine = create_engine(DATABASE_URL)
    st.success("Connected to Supabase via Supavisor! ✅")

    # Fetch data
    query = "SELECT * FROM product"  # Replace 'product' with your actual table name
    df = pd.read_sql(query, engine)

    # Display in Streamlit
    st.dataframe(df)

except Exception as e:
    st.error(f"Connection failed: {e}")
