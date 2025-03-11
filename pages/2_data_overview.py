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

if df is not None:
    st.write("✅ **Data loaded successfully!**")

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

    # Determine unit type (each, kg, litre)
    def get_unit(row):
        if row["Unit_each"] == 1:
            return "Each"
        elif row["Unit_kg"] == 1:
            return "Per kg"
        elif row["Unit_litre"] == 1:
            return "Per litre"
        return "Unknown"

    df["Unit Type"] = df.apply(get_unit, axis=1)

    # Select top 5 expensive products and include the unit type
    top_expensive = df.nlargest(5, "Price")[["Name", "Price", "Store_Name", "Unit Type"]]

    # Display as table
    st.table(top_expensive)

    # Function to create styled, minimal plots
    def create_styled_plot(fig, ax, title, xlabel, ylabel):
        fig.set_size_inches(6, 3)  # Smaller size for minimal look
        ax.set_title(title, fontsize=12, fontweight="bold", color="#333333")
        ax.set_xlabel(xlabel, fontsize=10, color="#555555")
        ax.set_ylabel(ylabel, fontsize=10, color="#555555")
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        plt.xticks(fontsize=9, color="#444444")
        plt.yticks(fontsize=9, color="#444444")
        plt.tight_layout()

    # 📊 Price Distribution Plot
    st.subheader("📊 Price Distribution")
    fig1, ax1 = plt.subplots()
    df["Price"].hist(bins=30, edgecolor="black", alpha=0.7, ax=ax1, color="#3498db")  # Blue bars
    create_styled_plot(fig1, ax1, "Distribution of Product Prices", "Price (£)", "Frequency")
    st.pyplot(fig1)

    # 📈 Price Trends Over Time
    st.subheader("📅 Price Trends Over Time")
    df["Date"] = pd.to_datetime(df[["Year", "Month", "Day"]])  # Create Date column
    avg_price_trend = df.groupby("Date")["Price"].mean()

    fig2, ax2 = plt.subplots()
    avg_price_trend.plot(ax=ax2, color="#2ecc71", linewidth=2)  # Green line
    create_styled_plot(fig2, ax2, "Average Price Over Time", "Date", "Average Price (£)")
    st.pyplot(fig2)

    # 🏪 Price Comparison Across Stores
    st.subheader("🏪 Price Comparison Across Stores")
    avg_price_per_store = df.groupby("Store_Name")["Price"].mean().sort_values()

    fig3, ax3 = plt.subplots()
    avg_price_per_store.plot(kind="barh", ax=ax3, color="#f39c12")  # Orange bars
    create_styled_plot(fig3, ax3, "Average Price Per Store", "Average Price (£)", "Store Name")
    st.pyplot(fig3)
else:
    st.write("⚠️ No data available.")

