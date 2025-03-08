import streamlit as st
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine

st.title("Hello World 👋")

# Initialize connection
conn = st.connection('supabase')

# Query your Supabase database
df = conn.query('SELECT * FROM mytable;')

# Display results
st.dataframe(df)

