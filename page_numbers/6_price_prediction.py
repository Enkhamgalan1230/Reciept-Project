import streamlit as st
import pandas as pd
import plotly.express as px

# Check if df is stored in session state
if "df" in st.session_state:
    df = st.session_state.df  # Retrieve stored data
else:
    st.warning("💡 Hint: No data available. Please visit the Data Fetcher page quickly and come back to this page.")
    st.stop()

st.title("Price Prediction", anchor=False)

with st.expander("💡How Does it work?"):
    st.write("""
        This page shows how food prices have changed over time and uses forecasts to predict future price trends. 
        It also highlights how prices usually rise or fall during seasonal events like Christmas or Easter, helping you plan smarter shopping.
             
        Historical data is provided by ONS(Office for National Statistics)
    """)


con1 = st.container(border=True)
con2 = st.container(border=True)
con3 = st.container(border=True)
con4 = st.container(border=True)


cpih = pd.read_csv("clean_cpih.csv")

# Melt wide format into long format
df_melted = cpih.melt(id_vars="Product", var_name="Date", value_name="Index")

# Create dropdown to select products
all_products = df_melted["Product"].unique().tolist()
# Ensure the 'Date' column is actually datetime
df_melted["Date"] = pd.to_datetime(df_melted["Date"], format="%Y %b", errors="coerce")

# Sort by date to help Plotly
df_melted = df_melted.sort_values("Date")
default_selection = ["Bread and cereals", "Meat", "Milk, cheese and eggs"]  # def
with con1:
    with st.expander("💡What is this?"):
        st.write("""
            The chart below illustrates the CPIH (Consumer Prices Index including Housing costs) trends for selected food categories over the past 14 months. Each line represents how the average price of a product category has changed relative to its baseline in 2015 (which is set to 100).
            For example, a value of 140 on the y-axis means the item has become 40% more expensive since 2015.
            Use this chart to compare how inflation has impacted different food categories. Sudden increases or consistent upward trends can signal rising costs, while stable or declining lines may indicate better value for budgeting.
        """)
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
                type="date",
                tickformat="%b %Y",
                tickmode="array",  
                tickvals=filtered_df["Date"].dropna().sort_values().unique(), 
                tickfont=dict(size=12)
            )
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select at least one product category to display the chart.")

    st.caption("📌 CPIH Index is relative to the base year (e.g., 2015 = 100). If a product is at 150, it means prices have risen 50% since 2015.")


df = pd.read_csv("arima_forecast_all_products.csv")
df["Date"] = pd.to_datetime(df["Date"])

with con2:

    
    with st.expander("💡What is this?"):
        st.write("""
            This chart uses the ARIMA model (AutoRegressive Integrated Moving Average) to forecast CPIH trends for the selected food category over the next 6 months. The solid line represents the predicted CPIH Index based on historical data, while the shaded area shows the confidence interval — a range of possible outcomes.
            * The Upper Bound indicates a best-case scenario (higher prices if inflation continues to rise).
            * The Lower Bound reflects a worst-case or drop scenario.
            
            This forecast helps you anticipate upcoming price movements, so you can make smarter decisions about budgeting and shopping — especially for items likely to increase soon.
        """)

    product = st.selectbox("Choose a product to view forecast:", df["Product"].unique())
    filtered = df[df["Product"] == product]

    fig = px.line(
        filtered,
        x="Date", y="Forecast",
        title=f"{product} – 6 Month ARIMA Forecast",
        markers=True
    )

    fig.add_scatter(x=filtered["Date"], y=filtered["Lower"], mode='lines', name="Lower Bound", line=dict(dash='dot'))
    fig.add_scatter(x=filtered["Date"], y=filtered["Upper"], mode='lines', name="Upper Bound", line=dict(dash='dot'))

    fig.update_layout(yaxis_title="CPIH Index", xaxis_title="Date")
    st.plotly_chart(fig, use_container_width=True)

    # Calculate percentage change between first and last forecast for each product
    latest_growth = (
        df.groupby("Product")
        .apply(lambda g: (g["Forecast"].iloc[-1] - g["Forecast"].iloc[0]) / g["Forecast"].iloc[0] * 100)
        .reset_index(name="Percent Change")
    )

    # Sort and get top 5
    top_risers = latest_growth.sort_values("Percent Change", ascending=False).head(5)
    top_risers.reset_index(drop=True, inplace=True)

    st.subheader("🔺 Top 5 Products with Highest Predicted Increase")
    st.dataframe(top_risers.style.format({"Percent Change": "{:.2f}%"}))

    fig = px.bar(top_risers, x="Product", y="Percent Change",
                title="Top 5 Forecasted Price Increases",
                labels={"Percent Change": "% Increase"},
                color="Percent Change")
    st.plotly_chart(fig, use_container_width=True)

with con3:

    def tag_occasion(date):
        if date.month == 12:
            return "Christmas"
        elif date.month in [3, 4]:
            return "Easter"
        elif date.month in [6, 7, 8]:
            return "Summer"
        elif date.month == 9:
            return "Back to School"
        elif date.month == 2:
            return "Valentine's Day"
        elif date.month == 10:
            return "Halloween"
        elif date.month == 11:
            return "Bonfire Night"
        else:
            return "Regular"

    df_melted["Occasion"] = df_melted["Date"].apply(tag_occasion)

    with st.expander("💡What is this?"):
        st.write("""
            This section reveals how average CPIH index values shift during seasonal occasions like Valentine’s Day, Easter, or Christmas compared to regular months. CPIH is an inflation index where a value of 150 means prices have risen 50% since 2015 — it's not the actual price, but a relative measure of cost change over time.
            * Top 5 Price Drops show products that typically become cheaper during the selected occasion — great for stocking up.
            * Top 5 Price Spikes highlight items that often see noticeable increases — it might be smarter to buy them ahead of time.

            Beneath the tables, the Seasonal Insight cards offer quick tips on items likely to remain stable or fluctuate, helping you make more informed shopping decisions based on past trends.
        """)

    # Occasion dropdown
    occasion = st.selectbox(
        "🎉 Select an Occasion:",
        options=[o for o in df_melted["Occasion"].unique() if o != "Regular"]
    )
    # Occasion vs. Regular comparison
    occasion_stats = df_melted.groupby(["Product", "Occasion"])["Index"].mean().reset_index()
    pivot = occasion_stats.pivot(index="Product", columns="Occasion", values="Index").fillna(0)

    if "Regular" in pivot.columns and occasion in pivot.columns:
        # Simplified display: only Regular, Occasion, and Change
        reduced = pivot[["Regular", occasion]].copy()
        safe_occasion = occasion.replace("'", "")  # or use any safer mapping
        reduced.columns = ["Regular CPIH Index", f"{occasion} CPIH Index"]

        # Calculate % change
        reduced[f"% Change {occasion} vs. Regular"] = (
            (reduced[f"{occasion} CPIH Index"] - reduced["Regular CPIH Index"]) / reduced["Regular CPIH Index"] * 100
        )

        reduced = reduced.reset_index()

        # Top 5 sorted
        top_discount = reduced.sort_values(f"% Change {occasion} vs. Regular").head(5)
        top_spike = reduced.sort_values(f"% Change {occasion} vs. Regular", ascending=False).head(5)

        st.markdown(f"### 👍 Biggest Price Drops – {occasion}")
        st.dataframe(top_discount.style.format({col: "{:.2f}" for col in reduced.columns if "CPIH" in col or "Change" in col}))
        st.markdown(f"### 👎 Biggest Price Spikes – {occasion}")
        st.dataframe(top_spike.style.format({col: "{:.2f}" for col in reduced.columns if "CPIH" in col or "Change" in col}))
        
    else:
        st.warning(f"Not enough data for {occasion} vs. Regular comparison.")


        
    rising = reduced[reduced[f"% Change {occasion} vs. Regular"] >= 2]
    falling = reduced[reduced[f"% Change {occasion} vs. Regular"] <= -2]
    stable = reduced[(reduced[f"% Change {occasion} vs. Regular"] > -2) & (reduced[f"% Change {occasion} vs. Regular"] < 2)]

    warnings = []

    # Add big risers
    for _, row in rising.head(3).iterrows():
        warnings.append(f"📈 **{row['Product']}** tends to increase by {row[f'% Change {occasion} vs. Regular']:.2f}% during **{occasion}**.")

    # Add big fallers
    for _, row in falling.head(3).iterrows():
        warnings.append(f"📉 **{row['Product']}** typically drops by {row[f'% Change {occasion} vs. Regular']:.2f}% during **{occasion}**.")

    for _, row in stable.head(2).iterrows():
        warnings.append(f"🔄 **{row['Product']}** remains fairly stable during **{occasion}**.")


    st.markdown("### 🧾 Seasonal Insight")
    st.caption("💡 Hint:🔻 for drops, 2.📈 for increases, 3.🔄 for stable")


    # Break warnings into rows of 4
    cols = st.columns(4)
    for i, warning in enumerate(warnings):
        with cols[i % 4].container(border=True):
            st.markdown(warning)

