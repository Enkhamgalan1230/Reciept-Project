import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time
from data_fetcher import fetch_data


st.dataframe(df.head())  # Show first few rows
