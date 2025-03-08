import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client

st.title("Hello World 👋")

# Initialize connection
@st.cache_resource
def init_connection():
    url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Perform query
@st.cache_data(ttl=600)
def run_query():
    response = supabase.table("Product").select("*").execute()
    
    # Debugging: Print raw response
    st.write("Raw Response:", response)

    # Convert to DataFrame
    if response.data:
        df = pd.DataFrame(response.data)
    else:
        df = pd.DataFrame(columns=["No data found"])  # Show empty DataFrame message

    return df

# Fetch and display data
df = run_query()
st.dataframe(df)