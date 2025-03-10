import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client

st.title("Hello World 👋")
''' 
# Fetch Data from Supabase Table
def fetch_data():
    response = supabase.table("your_table_name").select("*").execute()
    return response.data

# Insert Data into Supabase
def insert_data(name, age):
    response = supabase.table("your_table_name").insert({"name": name, "age": age}).execute()
    return response
'''
# Display Data
if st.button("Fetch Data"):
    data = fetch_data()
    st.write(data)