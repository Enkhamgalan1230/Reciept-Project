import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time
import matplotlib.pyplot as plt
import plotly.express as px


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

if df is not None:
    st.write("✅ **Data loaded successfully!**")

    # Show first few rows
    st.subheader("📊 Sample Data")
    st.dataframe(df.head(10))

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

    # Function to determine the unit type (Each, Per kg, Per litre)
    def get_unit(row):
        if row["Unit_each"] == 1:
            return "Each"
        elif row["Unit_kg"] == 1:
            return "Per kg"
        elif row["Unit_litre"] == 1:
            return "Per litre"
        return "Unknown"

    df["Unit Type"] = df.apply(get_unit, axis=1)

    # Drop exact duplicates (same product, price, store, and unit type)
    df_unique = df.drop_duplicates(subset=["Name", "Price", "Store_Name", "Unit Type"])

    # Get the Top 5 Most Expensive Products (without duplicate product names)
    top_expensive = df_unique.sort_values(by="Price", ascending=False).drop_duplicates(subset=["Name"]).head(5)

    # Select relevant columns
    top_expensive = top_expensive[["Name", "Price", "Store_Name", "Unit Type"]]

    # Display as table
    st.table(top_expensive)

    # 📊 Price Distribution Plot
    st.subheader("📊 Price Distribution")
    fig1 = px.histogram(df, x="Price", nbins=30, title="Distribution of Product Prices", 
                        color_discrete_sequence=["#3498db"], template="plotly_white")
    st.plotly_chart(fig1, use_container_width=True)

    # 📈 Price Trends Over Time
    st.subheader("📉 Price Trends Over Time")
    avg_price_trend = df.groupby("Date")["Price"].mean().reset_index()
    fig2 = px.line(avg_price_trend, x="Date", y="Price", title="Average Price Over Time", 
                line_shape="spline", color_discrete_sequence=["#2ecc71"], template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)

    # 🛍️ Average Price by Category
    st.subheader("🛍️ Average Price by Category")
    avg_price_category = df.groupby("Category")["Price"].mean().reset_index()
    fig3 = px.bar(avg_price_category, x="Category", y="Price", title="Average Price by Category", 
                color="Category", color_discrete_sequence=px.colors.qualitative.Vivid, template="plotly_white")
    st.plotly_chart(fig3, use_container_width=True)

    # 🏪 Price Comparison Across Stores
    st.subheader("🏪 Price Comparison Across Stores")
    avg_price_per_store = df.groupby("Store_Name")["Price"].mean().reset_index()
    fig4 = px.bar(avg_price_per_store, x="Store_Name", y="Price", title="Average Price Per Store", 
                color="Store_Name", color_discrete_sequence=px.colors.qualitative.Set2, template="plotly_white")
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.write("⚠️ No data available.")

