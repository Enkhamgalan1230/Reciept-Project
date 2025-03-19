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

# Get unique available dates
unique_dates = df["datetime"].unique()
latest_date = unique_dates.max()
second_latest_date = unique_dates[unique_dates != latest_date].max()  # Second latest date

# Filter data for the latest and second latest dates
df_latest = df[df["datetime"] == latest_date]
df_previous = df[df["datetime"] == second_latest_date]

# Allow user to select **one store** using `st.pills`
stores = df["Store_Name"].unique().tolist()
selected_store = st.pills("Pick a Supermarket", stores, selection_mode="single")

if selected_store:
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

    # Format prices and inflation
    df_inflation["Price_latest"] = df_inflation["Price_latest"].apply(lambda x: f"£{x:.2f}" if pd.notna(x) else "No Data")
    df_inflation["Inflation"] = df_inflation["Inflation"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "0.00%")

    # Display selected store title inside a **container with border**
    with st.container(border=True):
        st.markdown(f"## {selected_store}")

        # Use a **5-column layout** for better spacing
        columns = st.columns(5)
        for idx, row in df_inflation.iterrows():
            price_color = "green" if float(row["Inflation"].replace('%', '')) > 0 else "red"
            price_change = f"<span style='color:{price_color}; font-size: 14px; font-weight: bold;'>{row['Inflation']} {'🔺' if price_color == 'green' else '🔻'}</span>"

            # Place items in columns dynamically (cycling through the 5 columns)
            col = columns[idx % 5]

            # Wrap each category in a small, evenly spaced container
            with col.container(border=True, height=120, padding=10):
                col.markdown(f"<div style='text-align: center; font-weight: bold; font-size: 16px;'>{row['Subcategory'].replace('_', ' ').title()}</div>", unsafe_allow_html=True)
                col.markdown(f"<div style='text-align: center; font-size: 18px; font-weight: bold;'>{row['Price_latest']}</div>", unsafe_allow_html=True)
                col.markdown(f"<div style='text-align: center;'>{price_change}</div>", unsafe_allow_html=True)
