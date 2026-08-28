import streamlit as st
import pandas as pd

# Check if df is stored in session state
df = st.session_state.df

st.title("Price Inflation", anchor=False)

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

# Convert Year, Month, and Day columns into a single datetime column.
df["datetime"] = pd.to_datetime(df[["Year", "Month", "Day"]], errors="coerce")

# Allow user to select **one store** using `st.pills`
stores = df["Store_Name"].unique().tolist()
selected_store = st.pills("Pick a Supermarket to See Average Price Inflation", stores, selection_mode="single")

# If no store is selected, show a success message
if not selected_store:
    st.success("✅ Please choose a store to see the board")
    st.stop()

# Use the latest two snapshots available for this store, rather than the
# latest two dates globally. This handles stores with different update dates.
store_data = df[
    (df["Store_Name"] == selected_store)
    & df["datetime"].notna()
    & pd.to_numeric(df["Price"], errors="coerce").notna()
].copy()
store_data["Price"] = pd.to_numeric(store_data["Price"], errors="coerce")
store_data = store_data.dropna(subset=["Price"])
available_dates = sorted(store_data["datetime"].unique())
if len(available_dates) < 2:
    st.warning("There are not two valid price snapshots available for this store yet.")
    st.stop()

latest_date, previous_date = available_dates[-1], available_dates[-2]
df_latest_store = store_data[store_data["datetime"] == latest_date]
df_previous_store = store_data[store_data["datetime"] == previous_date]

# Compute the average price for each subcategory in the selected store
latest_prices = df_latest_store.groupby("Subcategory", as_index=False)["Price"].mean()
previous_prices = df_previous_store.groupby("Subcategory", as_index=False)["Price"].mean()

# Merge both datasets
df_inflation = latest_prices.merge(
    previous_prices,
    on="Subcategory",
    suffixes=("_latest", "_previous"),
    how="inner",
).dropna(subset=["Price_latest", "Price_previous"])
df_inflation = df_inflation[df_inflation["Price_previous"] > 0].copy()
df_inflation["Inflation"] = (
    (df_inflation["Price_latest"] - df_inflation["Price_previous"])
    / df_inflation["Price_previous"]
) * 100

if df_inflation.empty:
    st.info("No categories have valid prices in both of the latest snapshots for this store.")
    st.stop()

# Display selected store title inside a **container with border**
with st.container(border=True):
    st.markdown(f"## {selected_store}")
    st.caption(f"Comparing {previous_date:%d %b %Y} with {latest_date:%d %b %Y}")

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

