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


cpih = pd.read_csv("clean_cpih.csv")

# Melt wide format into long format
df_melted = cpih.melt(id_vars="Product", var_name="Date", value_name="Index")

# Convert Date to datetime
df_melted["Date"] = pd.to_datetime(df_melted["Date"], format="%Y %b")

# Streamlit caption for context


# Create dropdown to select products
all_products = df_melted["Product"].unique().tolist()
default_selection = ["Bread and cereals", "Meat", "Milk, cheese and eggs"]  # Adjust these

selected = st.multiselect(
    "Select food product categories to view inflation trends:",
    options=all_products,
    default=default_selection
)

# Filter and plot only selected items
if selected:
    filtered_df = df_melted[df_melted["Product"].isin(selected)]

    fig = px.line(filtered_df, x="Date", y="Index", color="Product",
                  title="CPIH Inflation Trend by Product")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="CPIH Index",
        xaxis_tickangle=-45,
        xaxis=dict(
            tickformat="%b %Y",  # 👈 Forces "Apr 2024", "May 2024", etc.
            tickmode="linear",   # 👈 Avoids skipping or auto-optimizing ticks
            tickfont=dict(size=12)
        )
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Please select at least one product category to display the chart.")

st.caption("📌 CPIH Index is relative to the base year (e.g., 2015 = 100). If a product is at 150, it means prices have risen 50% since 2015.")