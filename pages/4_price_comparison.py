import streamlit as st


popular_items = [
    "Chicken Breast", "Canned Tuna", "Long Grain Rice", "Penne Pasta", "Whole Grain Bread",
    "Olive Oil", "Eggs (6 pack)", "Ground Beef", "All Purpose Flour", "Salted Butter",
    "Semi Skimmed Milk", "Canned Sardines", "Cheddar Cheese", "Greek Yogurt", "Tomato Ketchup",
    "Breakfast Cereal", "Peanut Butter", "Frozen Mixed Vegetables", "Fresh Apples", "Carrots",
    "White Sugar", "Frozen French Fries", "Instant Coffee", "Toilet Paper", "Washing Liquid"
]


# Check if df is stored in session state
if "df" in st.session_state:
    df = st.session_state.df
else:
    st.write("⚠️ No data available. Please visit the Data Analysis page first.")

st.title("📊 Supermarket Price Comparison Dashboard")

# ✅ Step 1: Find the cheapest option per product
df_filtered = df[df["Product"].isin(popular_items)]
df_cheapest = df_filtered.groupby("Product").apply(lambda x: x.loc[x["Price"].idxmin()])

# ✅ Step 2: Display Key Metrics (Product Name + Cheapest Store)
st.subheader("💰 Cheapest Supermarket for Essential Groceries")

cols = st.columns(5)  # Create 5 columns for metrics

for index, (product, row) in enumerate(df_cheapest.iterrows()):
    with cols[index % 5]:  # Distribute across 5 columns
        st.metric(
            label=f"**{product}**",
            value=f"£{row['Price']:.2f}",
            delta=f"🛒 {row['Store']}"
        )

# ✅ Step 3: Display Price Trends Using Charts
st.subheader("📈 Price Trends Over Time")

chart_cols = st.columns(5)  # Create 5 columns for charts

# Iterate over products and create charts
for index, product in enumerate(popular_items):
    product_df = df[df["Product"] == product]

    if not product_df.empty:
        fig = px.line(
            product_df, x="Date", y="Price", color="Store",
            title=f"Price Trend: {product}",
            markers=True
        )

        fig.update_layout(yaxis_title="Price (£)", xaxis_title="Date", height=250)

        with chart_cols[index % 5]:  # Assign each chart to a column
            st.plotly_chart(fig, use_container_width=True)