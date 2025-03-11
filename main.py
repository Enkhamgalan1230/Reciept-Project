import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time

st.set_page_config(
        page_title="Home Page 🏠",
)
st.title("Welcome to Reciept 👋")


    