import streamlit as st
import pandas as pd
import datetime

# Check if df is stored in session state
if "df" in st.session_state:
    df = st.session_state.df  # Retrieve cached data
else:
    st.write("⚠️ No data available. Please visit the Data Analysis page first.")


st.title("📊 Price Prediction")
st.markdown("---")

st.subheader("🏆 Weekly Price inflation.")

# Convert date column to datetime format
df["Date"] = pd.to_datetime(df["Date"])

# Get the latest two unique dates
latest_date = df["Date"].max()
second_latest_date = df["Date"].nlargest(2).iloc[-1]  # Second latest date

# Filter data for both dates
df_latest = df[df["Date"] == latest_date]
df_previous = df[df["Date"] == second_latest_date]

# Get unique supermarket names
supermarkets = df["Store_Name"].unique().tolist()

# Store selection using st.pills (multi-select)
selected_stores = st.pills("Pick a Supermarket", supermarkets, selection_mode="multi")

# Filter data by selected supermarkets
if selected_stores:
    df_latest = df_latest[df_latest["Store_Name"].isin(selected_stores)]
    df_previous = df_previous[df_previous["Store_Name"].isin(selected_stores)]

# Calculate Inflation
df_inflation = df_latest.merge(df_previous, on=["Subcategory", "Store_Name"], suffixes=("_latest", "_previous"))
df_inflation["Inflation"] = ((df_inflation["Price_latest"] - df_inflation["Price_previous"]) / df_inflation["Price_previous"]) * 100

# Display inflation results
st.header("Average Price Changes")

# Format output for display
for _, row in df_inflation.iterrows():
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; width: 100%; padding: 10px; border-bottom: 1px solid #444;">
        <span style="font-weight: bold;">{row['Subcategory']}</span>
        <span style="font-weight: bold; color: {'red' if row['Inflation'] < 0 else 'green'};">
            {row['Price_latest']} ({row['Inflation']:.2f}% {"🔻" if row['Inflation'] < 0 else "🔺"})
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
            animation: slide 10s linear infinite;
        }
    </style>
    <div class="marquee">
        <div>
""", unsafe_allow_html=True)

# Generate sliding text for each subcategory
scrolling_text = "  |  ".join([f"{row['Subcategory']}: £{row['Price_latest']} ({row['Inflation']:.2f}%)" for _, row in df_inflation.iterrows()])
st.markdown(f'<div class="marquee"><div>{scrolling_text}</div></div>', unsafe_allow_html=True)
