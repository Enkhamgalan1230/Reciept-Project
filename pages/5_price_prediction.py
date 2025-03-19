import streamlit as st
import pandas as pd

# Check if df is stored in session state
if "df" in st.session_state:
    df = st.session_state.df  # Retrieve cached data
else:
    st.write("⚠️ No data available. Please visit the Data Analysis page first.")
    st.stop()

st.title("📊 Price Prediction")
st.markdown("---")
st.subheader("🏆 Weekly Average Price Inflation")

# Load Subcategories from CSV
subcategory_file = "subcategory.csv"
subcategories_df = pd.read_csv(subcategory_file)
subcategory_list = subcategories_df["Subcategory"].unique().tolist()

# Convert Year, Month, and Day columns into a single datetime column
df["datetime"] = pd.to_datetime(df[["Year", "Month", "Day"]])

# Get the latest available date
latest_date = df["datetime"].max()

# Filter data to only include rows from the latest date
df_latest = df[df["datetime"] == latest_date]

# Compute the average price for each store
average_prices = df_latest.groupby("Store_Name")["Price"].mean().reset_index()

# Display results
st.subheader("📌 Average Prices by Store (Latest Date)")

for _, row in average_prices.iterrows():
    st.markdown(f"**{row['Store_Name']}**: £{row['Price']:.2f}")