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
try:
    subcategories_df = pd.read_csv(subcategory_file)
    subcategory_list = subcategories_df["Subcategory"].unique().tolist()
except Exception as e:
    st.write(f"⚠️ Error loading subcategory file: {e}")
    subcategory_list = df["Subcategory"].unique().tolist()  # Fallback

# Convert Year, Month, and Day columns into a single datetime column
df["datetime"] = pd.to_datetime(df[["Year", "Month", "Day"]])

# Get the latest and second latest available dates
unique_dates = df["datetime"].unique()
latest_date = unique_dates.max()  # Latest available date
second_latest_date = unique_dates[unique_dates != latest_date].max()  # Second latest date

# Filter data for the latest and second latest dates
df_latest = df[df["datetime"] == latest_date]
df_previous = df[df["datetime"] == second_latest_date]

# Create a full Store-Subcategory grid to prevent missing entries
store_subcategory_grid = pd.MultiIndex.from_product(
    [df["Store_Name"].unique(), subcategory_list], 
    names=["Store_Name", "Subcategory"]
)

# Compute the average price for each subcategory in each store (latest & previous)
latest_prices = df_latest.groupby(["Store_Name", "Subcategory"])["Price"].mean().reset_index()
previous_prices = df_previous.groupby(["Store_Name", "Subcategory"])["Price"].mean().reset_index()

# Ensure all stores have all subcategories for both latest and previous data
latest_prices = latest_prices.set_index(["Store_Name", "Subcategory"]).reindex(store_subcategory_grid).reset_index()
previous_prices = previous_prices.set_index(["Store_Name", "Subcategory"]).reindex(store_subcategory_grid).reset_index()

# Merge latest and previous prices
df_inflation = latest_prices.merge(previous_prices, on=["Store_Name", "Subcategory"], suffixes=("_latest", "_previous"), how="outer")

# Fill missing prices with available data, set inflation to 0% when no previous data exists
df_inflation["Price_latest"].fillna(df_inflation["Price_previous"], inplace=True)  # If latest price is missing, use previous
df_inflation["Price_previous"].fillna(df_inflation["Price_latest"], inplace=True)  # If previous price is missing, use latest
df_inflation["Inflation"] = ((df_inflation["Price_latest"] - df_inflation["Price_previous"]) / df_inflation["Price_previous"]) * 100
df_inflation["Inflation"].fillna(0, inplace=True)  # If inflation cannot be calculated, set it to 0%

# Format prices and inflation
df_inflation["Price_latest"] = df_inflation["Price_latest"].apply(lambda x: f"£{x:.2f}" if pd.notna(x) else "No Data")
df_inflation["Price_previous"] = df_inflation["Price_previous"].apply(lambda x: f"£{x:.2f}" if pd.notna(x) else "No Data")
df_inflation["Inflation"] = df_inflation["Inflation"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "0.00%")

# Display results
st.subheader("📌 Inflation Report by Store & Subcategory")

for store in df_inflation["Store_Name"].unique():
    st.markdown(f"### 🏪 {store}")  # Store name as a header
    store_data = df_inflation[df_inflation["Store_Name"] == store]
    
    for _, row in store_data.iterrows():
        st.markdown(f"- **{row['Subcategory']}**: {row['Price_latest']} (Inflation: {row['Inflation']})")
