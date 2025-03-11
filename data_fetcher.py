import time
import pandas as pd
import streamlit as st
from streamlit.connections import SupabaseConnection

# Initialize Supabase connection
conn = st.connection("supabase", type=SupabaseConnection)

@st.cache_data
def fetch_data_with_progress():
    """Fetch data from Supabase with a progress bar if needed."""
    try:
        # Step 1: Get total row count dynamically
        row_count_result = conn.table("Product").select("*", count="exact", head=True).execute()
        max_rows = row_count_result.count
        batch_size = 1000
        total_batches = (max_rows + batch_size - 1) // batch_size  # Round up

        # Progress bar (only shows if used in `2_second.py`)
        progress_bar = st.progress(0)
        progress_text = st.empty()

        all_rows = []
        offset = 0

        for batch in range(1, total_batches + 1):
            try:
                # Fetch batch of data
                rows = conn.table("Product").select("*").range(offset, offset + batch_size - 1).execute()

                if not rows.data:
                    break

                all_rows.extend(rows.data)
                offset += batch_size

                # Update progress bar
                progress_percentage = batch / total_batches
                progress_bar.progress(min(progress_percentage, 1.0))

                progress_text.write(f"Fetching batch {batch}/{total_batches}...")

                time.sleep(0.5)  # Avoid request overload

            except Exception as e:
                st.write(f"Error at batch {batch}, offset {offset}: {e}")
                break

        df = pd.DataFrame(all_rows)
        return df

    except Exception as e:
        st.write(f"Error fetching data: {e}")
        return None
