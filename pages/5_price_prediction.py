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
st.subheader("🏆 Weekly Price Inflation")

# Load Subcategories from CSV
subcategory_file = "subcategory.csv"  # Adjust the path if needed
try:
    subcategories_df = pd.read_csv(subcategory_file)
    subcategory_list = subcategories_df["Subcategory"].unique().tolist()
except Exception as e:
    st.write(f"⚠️ Error loading subcategory file: {e}")
    subcategory_list = df["Subcategory"].unique().tolist()  # Fallback

# Convert Year, Month, and Day columns into a single datetime column
df["datetime"] = pd.to_datetime(df[["Year", "Month", "Day"]])

# Get the latest two unique dates
latest_date = df["datetime"].max()
second_latest_date = df["datetime"].nlargest(2).iloc[-1]  # Second latest date

# Filter data for both dates
df_latest = df[df["datetime"] == latest_date]
df_previous = df[df["datetime"] == second_latest_date]

# Drop temporary datetime column
df.drop(columns=["datetime"], inplace=True)

# Get unique supermarket names
supermarkets = df["Store_Name"].unique().tolist()

# Store selection using st.pills (multi-select)
selected_stores = st.pills("Pick a Supermarket", supermarkets, selection_mode="multi")

# Filter data by selected supermarkets
if selected_stores:
    df_latest = df_latest[df_latest["Store_Name"].isin(selected_stores)]
    df_previous = df_previous[df_previous["Store_Name"].isin(selected_stores)]

# Calculate Inflation with Fixes
df_inflation = df_latest.merge(df_previous, on=["Subcategory", "Store_Name"], suffixes=("_latest", "_previous"), how="outer")

# Fill missing prices with previous known values
df_inflation["Price_latest"] = df_inflation["Price_latest"].fillna(df_inflation["Price_previous"])
df_inflation["Price_previous"] = df_inflation["Price_previous"].fillna(df_inflation["Price_latest"])

# Avoid division by zero
df_inflation["Inflation"] = ((df_inflation["Price_latest"] - df_inflation["Price_previous"]) / df_inflation["Price_previous"]) * 100
df_inflation["Inflation"].replace([float("inf"), -float("inf")], 0, inplace=True)

# Group by Subcategory to avoid duplicates
df_inflation = df_inflation.groupby("Subcategory", as_index=False).agg({
    "Price_latest": "mean",
    "Inflation": "mean"
})

# Display inflation results
st.header("Average Price Changes")
for _, row in df_inflation.iterrows():
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; width: 100%; padding: 10px; border-bottom: 1px solid #444;">
        <span style="font-weight: bold;">{row['Subcategory']}</span>
        <span style="font-weight: bold; color: {'red' if row['Inflation'] < 0 else 'green'};">
            £{row['Price_latest']:.2f} ({row['Inflation']:.2f}% {"🔻" if row['Inflation'] < 0 else "🔺"})
        </span>
    </div>
    """, unsafe_allow_html=True)

# Sliding Ticker for Subcategories
st.markdown("""
    <style>
        @keyframes slide {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
        .marquee {
            white-space: nowrap;
            overflow: hidden;
            position: relative;
            width: 100%;
        }
        .marquee div {
            display: inline-block;
            animation: slide 15s linear infinite;
        }
    </style>
""", unsafe_allow_html=True)

# Generate sliding text for each subcategory
scrolling_text = "  |  ".join([f"{row['Subcategory']}: £{row['Price_latest']:.2f} ({row['Inflation']:.2f}%)" for _, row in df_inflation.iterrows()])
st.markdown(f'<div class="marquee"><div>{scrolling_text}</div></div>', unsafe_allow_html=True)
