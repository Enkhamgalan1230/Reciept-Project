import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Price Prediction", anchor=False)


# Check if df is stored in session state
if "df" in st.session_state:
    df = st.session_state.df  # Retrieve stored data
    st.write("Nothing here yet!")
else:
    st.warning("💡 Hint: No data available. Please visit the Data Fetcher page quickly and come back to this page.")


data = pd.read_csv("clean_cpih.csv")

st.write("Columns in the loaded DataFrame:", df.columns.tolist())

# Melt wide format into long format
df_melted = df.melt(id_vars="Product", var_name="Date", value_name="Index")

# Convert Date to datetime for plotting
df_melted["Date"] = pd.to_datetime(df_melted["Date"], format="%Y %b")

st.caption("📌 CPIH Index is relative to the base year (e.g., 2015 = 100). If a product is at 150, it means prices have risen 50% since 2015.")
fig = px.line(
    df_melted,
    x="Date",
    y="Index",
    color="Product",
    title="Food Inflation Trends (CPIH)",
)

# Filter top N by latest inflation
top_n = df_melted[df_melted["Date"] == df_melted["Date"].max()]
top_10 = top_n.sort_values("Index", ascending=False)["Product"].unique()[:10]
df_top10 = df_melted[df_melted["Product"].isin(top_10)]

fig = px.line(df_top10, x="Date", y="Index", color="Product",
              title="Top 10 Most Inflated Food Products (CPIH)")
fig.update_layout(xaxis_title="Date", yaxis_title="CPIH Index")
fig.show()
