import time
import pandas as pd
import streamlit as st
from streamlit.connections import SupabaseConnection

# Initialize Supabase connection
conn = st.connection("supabase", type=SupabaseConnection)

@st.cache_data
def fetch_data():
    try:
        # Step 1: Get total row count dynamically
        row_count_result = conn.table("Product").select("*", count="exact", head=True).execute()
        max_rows = row_count_result.count
        st.write(f"There are {max_rows} rows currently in the database.")

        # Step 2: Fetch data with pagination
        batch_size = 1000
        total_batches = (max_rows + batch_size - 1) // batch_size

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

                progress_text.write(f"Fetching batch {batch}/{total_batches}...")

                time.sleep(0.5)

            except Exception as e:
                st.write(f"Error at batch {batch}, offset {offset}: {e}")
                break

        df = pd.DataFrame(all_rows)
        st.write("✅ Data fetching completed!")

        return df

    except Exception as e:
        st.write(f"Error fetching data: {e}")
        return None
