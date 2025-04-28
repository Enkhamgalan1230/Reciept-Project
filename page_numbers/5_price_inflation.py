import streamlit as st
import pandas as pd

# Check if df is stored in session state
if "df" in st.session_state:
    df = st.session_state.df  # Retrieve cached data
else:
    st.warning("💡 Hint: No data available. Please visit the Data Fetcher page quickly and come back to this page.")
    st.stop()

st.title("💷 Price Inflation", anchor=False)

with st.expander("💡How Does it work"):
    st.write("""
        This page shows how average prices for different food categories have changed over the past week at your chosen supermarket. 
        It helps you spot which types of groceries have gone up or down in price, so you can plan your shopping smarter.
    """)
st.subheader("Inflation Board", anchor=False)

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

# Get unique available dates
unique_dates = df["datetime"].unique()
latest_date = unique_dates.max()
second_latest_date = unique_dates[unique_dates != latest_date].max()  # Second latest date

# Filter data for the latest and second latest dates
df_latest = df[df["datetime"] == latest_date]
df_previous = df[df["datetime"] == second_latest_date]

# Allow user to select **one store** using `st.pills`
stores = df["Store_Name"].unique().tolist()
selected_store = st.pills("Pick a Supermarket to See Average Price Inflation", stores, selection_mode="single")

# If no store is selected, show a success message
if not selected_store:
    st.success("✅ Please choose a store to see the board")
    st.stop()

# Filter data for the selected store
df_latest_store = df_latest[df_latest["Store_Name"] == selected_store]
df_previous_store = df_previous[df_previous["Store_Name"] == selected_store]

# Compute the average price for each subcategory in the selected store
latest_prices = df_latest_store.groupby("Subcategory")["Price"].mean().reset_index()
previous_prices = df_previous_store.groupby("Subcategory")["Price"].mean().reset_index()

# Merge both datasets
df_inflation = latest_prices.merge(previous_prices, on="Subcategory", suffixes=("_latest", "_previous"), how="outer")

# Handle missing data by filling with available values and setting inflation to 0 if missing
df_inflation["Price_latest"].fillna(df_inflation["Price_previous"], inplace=True)
df_inflation["Price_previous"].fillna(df_inflation["Price_latest"], inplace=True)
df_inflation["Inflation"] = ((df_inflation["Price_latest"] - df_inflation["Price_previous"]) / df_inflation["Price_previous"]) * 100
df_inflation["Inflation"].fillna(0, inplace=True)

# Display selected store title inside a **container with border**
with st.container(border=True):
    st.markdown(f"## {selected_store}")

    # Use a **5-column layout** for better spacing
    columns = st.columns(5)
    for idx, row in df_inflation.iterrows():
        col = columns[idx % 5]

        # Wrap each category in a small, evenly spaced container
        with col.container(border=True):
            st.metric(
                label=row["Subcategory"].replace("_", " ").title(),  # Format category names
                value=f"£{row['Price_latest']:.2f}",
                delta=f"{row['Inflation']:.2f}%" if row['Inflation'] != 0 else "0.00%",
                delta_color = 'inverse'
            )
    
st.caption("📌 Prices and categories are based on the latest available data and previous week's data.")

