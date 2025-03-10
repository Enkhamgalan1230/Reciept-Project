import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time

st.title("Hello World 👋")

# Initialize Supabase connection
conn = st.connection("supabase", type=SupabaseConnection)


# Step 1: Get total row count dynamically
try:
    row_count_result = conn.table("Product").select("*", count="exact", head=True).execute()
    max_rows = row_count_result.count  # Extract total row count
    st.write(f"There are {max_rows} rows currentcly in database.")  # Debugging
    st.write(f"There is a 1000 rows limit to fetch the data from the database and it takes approximately 0.85seconds. So please bare with us 😊")
except Exception as e:
    st.write(f"Error fetching row count: {e}")
    max_rows = None

# Step 2: Fetch data with pagination and time estimation
if max_rows:
    batch_size = 1000  # Supabase limits max 1000 per request
    offset = 0
    all_rows = []
    
    start_time = time.time()  # Record start time

    while len(all_rows) < max_rows:
        try:
            batch_start_time = time.time()  # Start time for this batch

            # Fetch batch of data
            rows = conn.table("Product").select("*").range(offset, offset + batch_size - 1).execute()

            # If no more data, stop fetching
            if not rows.data:
                #st.write(f"Stopped fetching at offset {offset}")
                break

            # Append batch while ensuring we don’t exceed max_rows
            all_rows.extend(rows.data[: max_rows - len(all_rows)])

            # Move to next batch
            offset += batch_size

            # Calculate elapsed time and estimated remaining time
            elapsed_time = time.time() - start_time
            avg_time_per_batch = elapsed_time / (offset / batch_size)  # Average time per batch
            remaining_batches = (max_rows - len(all_rows)) / batch_size
            estimated_time_remaining = avg_time_per_batch * remaining_batches

            # Debugging: Print progress and estimated time remaining
            # **Rate limit: Add delay to avoid request overload**
            time.sleep(0.5)

        except Exception as e:
            st.write(f"Error at offset {offset}: {e}")
            break  # Stop fetching on error to prevent excessive requests

    # Convert list to DataFrame
    df = pd.DataFrame(all_rows)

    # Display total number of rows
    total_time_taken = time.time() - start_time
    st.write(f"Total number of rows fetched: {df.shape[0]}")
    st.write(f"Total time taken: {total_time_taken:.2f} seconds")
