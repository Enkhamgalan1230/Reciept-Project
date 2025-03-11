import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time


st.title("📊 Data")

st.markdown("---")


# Initialize Supabase connection
conn = st.connection("supabase", type=SupabaseConnection)

# Only fetch data if it's not already stored in session state
if "df" not in st.session_state:
    @st.cache_data  # Cache the fetched data
    def fetch_data():
        try:
            # Step 1: Get total row count dynamically
            row_count_result = conn.table("Product").select("*", count="exact", head=True).execute()
            max_rows = row_count_result.count
            st.write(f"There are {max_rows} rows currently in the database.")
            st.write("#### We are using Supabase and there is a 1000-row limit per request, so fetching will take some time. "
            " Please bare with us 😊")

            # Step 2: Fetch data with pagination
            batch_size = 1000
            total_batches = (max_rows + batch_size - 1) // batch_size  # Round up

            # Create progress bar
            progress_bar = st.progress(0)  
            progress_text = st.empty()  

            all_rows = []
            offset = 0

            for batch in range(1, total_batches + 1):
                try:
                    rows = conn.table("Product").select("*").range(offset, offset + batch_size - 1).execute()

                    if not rows.data:
                        break

                    all_rows.extend(rows.data)
                    offset += batch_size

                    # Update progress bar
                    progress_percentage = batch / total_batches
                    progress_bar.progress(min(progress_percentage, 1.0))

                    # Update progress text
                    progress_text.write(f"Fetching batch {batch}/{total_batches}...")

                    time.sleep(0.5)  # Rate limit

                except Exception as e:
                    st.write(f"Error at batch {batch}, offset {offset}: {e}")
                    break

            df = pd.DataFrame(all_rows)
            st.write("✅ Data fetching completed!")
            return df

        except Exception as e:
            st.write(f"Error fetching data: {e}")
            return None

    # Fetch and store in session state
    df = fetch_data()
    st.session_state.df = df  # Store for later use
else:
    df = st.session_state.df  # Load cached data

# Display fetched data
if df is not None:
    st.write("✅ Data loaded successfully!")
    st.dataframe(df.head())  # Show first few rows
else:
    st.write("⚠️ No data available.")