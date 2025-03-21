import streamlit as st
import mysql.connector
import pandas as pd
import supabase
import time
import matplotlib.pyplot as plt
import plotly.express as px
import random
from wordcloud import WordCloud
from collections import Counter
import re

# Check if df is stored in session state
if "df" in st.session_state:
    df = st.session_state.df  # Retrieve cached data
else:
    st.warning("💡 Hint: No data available. Please visit the Data Fetcher page quickly and come back to this page.")
    st.stop()

st.title("📈 Data Analysis", anchor=False)
st.markdown("---")

# 🔹 Create "Date" Column
if {"Year", "Month", "Day"}.issubset(df.columns):
    df["Date"] = pd.to_datetime(df[["Year", "Month", "Day"]], errors="coerce")

# 🔹 Display Key Metrics
st.subheader("📈 Dataset Overview", anchor=False)
col1, col2, col3 = st.columns(3)
col1.metric("Total Products In Database Right Now:", f"{df.shape[0]:,}")
col2.metric("Unique Stores", df["Store_Name"].nunique())
col3.metric("Price Range", f"£{df['Price'].min():.2f} - £{df['Price'].max():.2f}")

# 🔹 Show Sample Data
st.subheader("📋 Sample Data", anchor=False)
# Shuffle and select 10 random rows
sample_df = df.sample(n=10, random_state=42)  # You can remove 'random_state' for full randomness
st.dataframe(sample_df)
# 🔹 Top 5 Most Expensive Products
st.markdown("---")
st.subheader("💰 Top 5 Most Expensive Products", anchor=False)

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
st.subheader("🏬 Select Store to View Their Most Expensive Items", anchor=False)

# Get unique store names
stores = df_unique["Store_Name"].unique()

# Use st.pills for store selection
#selected_store = st.radio("Choose a store:", stores, horizontal=True)
selected_store = st.pills("Choose a store:", stores)


# Filter top 5 most expensive for selected store
if selected_store:
    st.subheader(f"💸 {selected_store}'s Most Expensive Products", anchor=False)
    top_store = df_unique[df_unique["Store_Name"] == selected_store].sort_values(by="Price", ascending=False).head(5)
    top_store = top_store[["Name", "Price", "Unit Type"]]
    st.table(top_store)

# 📊 Price Distribution Plot
st.markdown("---")
st.subheader("📊 Price Distribution", anchor=False)
fig1 = px.histogram(df, x="Price", nbins=30, title="Distribution of Product Prices", 
                    color_discrete_sequence=["#3498db"], template="plotly_white")
st.plotly_chart(fig1, use_container_width=True)

# 📉 Price Trends Over Time (Fix KeyError)
st.markdown("---")
st.subheader("📉 Price Trends Over Time", anchor=False)

if "Date" in df.columns and not df["Date"].isnull().all():
    avg_price_trend = df.groupby("Date")["Price"].mean().reset_index()
    fig2 = px.line(avg_price_trend, x="Date", y="Price", title="Average Price Over Time",
                    line_shape="spline", color_discrete_sequence=["#2ecc71"], template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.error("❌ No valid 'Date' column found. Ensure 'Year', 'Month', and 'Day' exist in the dataset.")

# 🛍️ Average Price by Category
st.markdown("---")
st.subheader("🛍️ Average Price by Category", anchor=False)
avg_price_category = df.groupby("Category")["Price"].mean().reset_index()
fig3 = px.bar(avg_price_category, x="Category", y="Price", title="Average Price by Category",
                color="Category", color_discrete_sequence=px.colors.qualitative.Vivid, template="plotly_white")
st.plotly_chart(fig3, use_container_width=True)

# 🏪 Price Comparison Across Stores
st.markdown("---")
st.subheader("🏪 Price Comparison Across Stores", anchor=False)
avg_price_per_store = df.groupby("Store_Name")["Price"].mean().reset_index()
fig4 = px.bar(avg_price_per_store, x="Store_Name", y="Price", title="Average Price Per Store",
                color="Store_Name", color_discrete_sequence=px.colors.qualitative.Set2, template="plotly_white")
st.plotly_chart(fig4, use_container_width=True)


def generate_wordcloud(df):
    # Combine all product names into a single text
    text = " ".join(df["Name"].dropna())

    # Remove special characters and numbers
    text = re.sub(r"[^a-zA-Z\s]", "", text)

    # Convert to lowercase and split words
    words = text.lower().split()

    # Define stopwords to exclude common words (can be expanded)
    stopwords = set(["the", "and", "for", "with", "per", "of", "in", "to", "a", "kg", "litre", "each"])

    # Filter words (remove stopwords)
    filtered_words = [word for word in words if word not in stopwords]

    # Create Word Cloud
    wordcloud = WordCloud(
        width=800, height=400,
        background_color="white",
        colormap="coolwarm",
        max_words=100
    ).generate(" ".join(filtered_words))

    return wordcloud

# 🔹 Streamlit App UI
st.markdown("---")
st.subheader("📌 Most Common Words in Product Names", anchor=False)

# Generate and display word cloud
wordcloud = generate_wordcloud(df)

fig, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)