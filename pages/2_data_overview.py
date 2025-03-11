import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time
import matplotlib.pyplot as plt


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
            st.write("#### We are using Supabase and there is a 1000-row limit per request, so fetching will take tiny bit of time. "
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
    # Show first few rows
    st.subheader("📊 Sample Data")
    st.dataframe(df.head())

    # Show key statistics
    st.subheader("📈 Dataset Overview")
    num_products = df.shape[0]
    num_stores = df["Store_Name"].nunique()
    price_range = (df["Price"].min(), df["Price"].max())

    st.write(f"- **Total Products:** {num_products}")
    st.write(f"- **Number of Stores:** {num_stores}")
    st.write(f"- **Price Range:** £{price_range[0]:.2f} - £{price_range[1]:.2f}")

    # Top 5 Most Expensive Products
    st.subheader("💰 Top 5 Most Expensive Products")
    top_expensive = df.nlargest(5, "Price")[["Name", "Price", "Store_Name"]]
    st.table(top_expensive)

    # Price Distribution Plot
    st.subheader("📊 Price Distribution")
    fig, ax = plt.subplots()
    df["Price"].hist(bins=30, edgecolor="black", alpha=0.7, ax=ax)
    ax.set_xlabel("Price (£)")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of Product Prices")
    st.pyplot(fig)

    # Price Trends Over Time
    st.subheader("📅 Price Trends Over Time")
    df["Date"] = pd.to_datetime(df[["Year", "Month", "Day"]])  # Create Date column
    avg_price_trend = df.groupby("Date")["Price"].mean()

    fig, ax = plt.subplots()
    avg_price_trend.plot(ax=ax)
    ax.set_xlabel("Date")
    ax.set_ylabel("Average Price (£)")
    ax.set_title("Average Price Over Time")
    st.pyplot(fig)

    # Price Comparison Across Stores
    st.subheader("🏪 Price Comparison Across Stores")
    avg_price_per_store = df.groupby("Store_Name")["Price"].mean().sort_values()

    fig, ax = plt.subplots()
    avg_price_per_store.plot(kind="barh", ax=ax, color="skyblue")
    ax.set_xlabel("Average Price (£)")
    ax.set_ylabel("Store Name")
    ax.set_title("Average Price Per Store")
    st.pyplot(fig)
else:
    st.write("⚠️ No data available.")

