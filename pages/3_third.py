import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time

# Initialize Supabase connection
conn = st.connection("supabase", type=SupabaseConnection)

# Function to fetch data (runs only once)
@st.cache_data  # Caches the result, preventing re-fetching across pages
def fetch_data():
    try:
        # Step 1: Get total row count dynamically
        row_count_result = conn.table("Product").select("*", count="exact", head=True).execute()
        max_rows = row_count_result.count  # Extract total row count
        st.write(f"There are {max_rows} rows currently in the database.")
        st.write("There is a 1000-row limit per request, so fetching will take some time. 😊")
        
        # Step 2: Fetch data with pagination
        batch_size = 1000  # Supabase allows max 1000 per request
        total_batches = (max_rows + batch_size - 1) // batch_size  # Ensures we round up

        # Create progress bar
        progress_bar = st.progress(0)  # Initial progress
        progress_text = st.empty()  # Placeholder for progress text

        all_rows = []
        offset = 0

        for batch in range(1, total_batches + 1):
            try:
                # Fetch batch of data
                rows = conn.table("Product").select("*").range(offset, offset + batch_size - 1).execute()

                # If no more data, stop fetching
                if not rows.data:
                    break

                # Append batch while ensuring we don’t exceed max_rows
                all_rows.extend(rows.data)

                # Move to next batch
                offset += batch_size

                # Update progress bar (each fetch = 1 step)
                progress_percentage = batch / total_batches
                progress_bar.progress(min(progress_percentage, 1.0))  # Ensure max value is 100%

                # Update progress text
                progress_text.write(f"Fetching batch {batch}/{total_batches}...")

                # **Rate limit: Add delay to avoid request overload**
                time.sleep(0.5)

            except Exception as e:
                st.write(f"Error at batch {batch}, offset {offset}: {e}")
                break  # Stop fetching on error

        # Convert list to DataFrame
        df = pd.DataFrame(all_rows)
        st.write("✅ Data fetching completed!")

        return df  # Cache the DataFrame

    except Exception as e:
        st.write(f"Error fetching data: {e}")
        return None

# Load data (runs only once per session)
df = fetch_data()

# Display fetched data
if df is not None:
    st.write("✅ Data loaded successfully!")
    st.dataframe(df.head())  # Show first few rows
else:
    st.write("⚠️ No data available.")

    st.write(df.head())
    st.write(df.tail())