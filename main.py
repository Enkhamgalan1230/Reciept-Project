import streamlit as st
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client

st.title("Hello World 👋")

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query():
    response = supabase.table("Product").select("*").execute()
    
    # Convert response to DataFrame
    if response.data:  # Ensure data is not empty
        df = pd.DataFrame(response.data)
    else:
        df = pd.DataFrame()  # Return empty DataFrame if no data

    return df

# Get the DataFrame
df = run_query()

# Display DataFrame in Streamlit
st.dataframe(df)