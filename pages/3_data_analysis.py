import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time
import matplotlib.pyplot as plt
import plotly.express as px
import random

# Check if df is stored in session state
if "df" in st.session_state:
    df = st.session_state.df  # Retrieve cached data
else:
    st.write("⚠️ No data available. Please visit the Data Fetcher page first.")
    st.stop()

st.title("📈 Data Analysis")
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
# Shuffle and select 10 random rows
sample_df = df.sample(n=10, random_state=42)  # You can remove 'random_state' for full randomness
st.dataframe(sample_df)
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

# 🔹 Store Selection for Most Expensive Items
st.subheader("🏬 Select Store to View Most Expensive Items")

# Get unique store names
stores = df_unique["Store_Name"].unique()

# Use st.pills for store selection
#selected_store = st.radio("Choose a store:", stores, horizontal=True)
selected_store = st.pills("Choose a store:", stores)


# Filter top 5 most expensive for selected store
if selected_store:
    st.subheader(f"💸 {selected_store}'s Most Expensive Products")
    top_store = df_unique[df_unique["Store_Name"] == selected_store].sort_values(by="Price", ascending=False).head(5)
    top_store = top_store[["Name", "Price", "Unit Type"]]
    st.table(top_store)

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


