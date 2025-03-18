import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time
import matplotlib.pyplot as plt
import plotly.express as px
import openai
import random


st.title("📊 Data")

st.markdown("---")

def get_fun_fact():
    # List of supermarket names
    supermarkets = ["Tesco", "Sainsbury's", "Morrisons", "Asda", "Aldi"]

    # Randomly choose one supermarket
    chosen_store = random.choice(supermarkets)

    # ChatGPT prompt
    prompt = f"Give me a short, fun, and interesting fact or statistic about {chosen_store} supermarket."

    # OpenAI API Call
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]  # Extract ChatGPT's response


# Initialize Supabase connection
conn = st.connection("supabase", type=SupabaseConnection)

# Only fetch data if it's not already in session state
if "df" not in st.session_state:
    @st.cache_data  # Cache the fetched data
    def fetch_data():
        try:
            # Step 1: Get total row count dynamically
            row_count_result = conn.table("Product").select("*", count="exact", head=True).execute()
            max_rows = row_count_result.count
            st.write(f"There are {max_rows} rows currently in the database.")

            # Step 2: Fetch data in batches (1000 rows per request)
            batch_size = 1000
            total_batches = (max_rows + batch_size - 1) // batch_size  # Round up

            # Progress Bar
            progress_bar = st.progress(0)  
            progress_text = st.empty()  
            fun_fact_box = st.empty()  # Empty box for updating facts

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

                    # Update fetching status
                    progress_text.write(f"Fetching batch {batch}/{total_batches}...")

                    # 🛒 Generate and Display Fun Fact about a supermarket
                    fun_fact = get_fun_fact()
                    fun_fact_box.write(f"🛍️ **Fun Fact:** {fun_fact}")

                    time.sleep(5)  # Wait 5 seconds before next batch

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
    st.markdown("---")

    # 🔹 Create "Date" Column
    if {"Year", "Month", "Day"}.issubset(df.columns):
        df["Date"] = pd.to_datetime(df[["Year", "Month", "Day"]], errors="coerce")

    # 🔹 Display Key Metrics
    st.subheader("📈 Dataset Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Products In Database Right Now:", f"{df.shape[0]:,}")
    col2.metric("Unique Stores", df["Store_Name"].nunique())
    col3.metric("Price Range", f"£{df['Price'].min():.2f} - £{df['Price'].max():.2f}")

    # 🔹 Show Sample Data
    st.subheader("📋 Sample Data")
    st.dataframe(df.head(10))

    # 🔹 Top 5 Most Expensive Products
    st.subheader("💰 Top 5 Most Expensive Products")

    # Determine Unit Type
    def get_unit(row):
        if row["Unit_each"] == 1:
            return "Each"
        elif row["Unit_kg"] == 1:
            return "Per kg"
        elif row["Unit_litre"] == 1:
            return "Per litre"
        return "Unknown"

    df["Unit Type"] = df.apply(get_unit, axis=1)

    # Remove duplicates & get top expensive products
    df_unique = df.drop_duplicates(subset=["Name", "Price", "Store_Name", "Unit Type"])
    top_expensive = df_unique.sort_values(by="Price", ascending=False).drop_duplicates(subset=["Name"]).head(5)
    top_expensive = top_expensive[["Name", "Price", "Store_Name", "Unit Type"]]

    st.table(top_expensive)

    # 📊 Price Distribution Plot
    st.subheader("📊 Price Distribution")
    fig1 = px.histogram(df, x="Price", nbins=30, title="Distribution of Product Prices", 
                        color_discrete_sequence=["#3498db"], template="plotly_white")
    st.plotly_chart(fig1, use_container_width=True)

    # 📉 Price Trends Over Time (Fix KeyError)
    st.subheader("📉 Price Trends Over Time")

    if "Date" in df.columns and not df["Date"].isnull().all():
        avg_price_trend = df.groupby("Date")["Price"].mean().reset_index()
        fig2 = px.line(avg_price_trend, x="Date", y="Price", title="Average Price Over Time",
                       line_shape="spline", color_discrete_sequence=["#2ecc71"], template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.error("❌ No valid 'Date' column found. Ensure 'Year', 'Month', and 'Day' exist in the dataset.")

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


