import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time
import matplotlib.pyplot as plt
import plotly.express as px


product_mapping = {
    "chicken breast 1kg" : {
        "tesco" : "Tesco British Chicken Breast Fillets 950G",
        "asda" : "ASDA Tender Chicken Breast Fillets",
        "aldi" : "Shazans Chicken Breast Fillets 950g",
        "waitrose" : "Essential Chicken Breast Fillets",
        "Sainsburys" : "Sainsbury's British Fresh Chicken Breast Fillets Skinless & Boneless 1kg"
    },
    "Canned Tuna" : {
        "tesco" : "Stockwell & Co Tuna Chunks In Brine 145G",
        "asda" : "ASDA Skipjack Tuna Chunks in Brine",
        "aldi" : "Everyday Essentials Tuna Chunks In Brine 145g",
        "waitrose" : "Essential MSC Tuna Chunks in Spring Water",
        "Sainsburys" : "Sainsbury's Tuna Chunks in Brine 145g"
    },
    "Long Grain Rice" : {
        "tesco" : "Tesco Easy Cook Long Grain Rice 1Kg",
        "asda" : "ASDA Long Grain White Rice 1kg",
        "aldi" : "Worldwide Foods Easy Cook Long Grain Rice 1kg",
        "waitrose" : "Essential Long Grain Rice Easy Cook",
        "Sainsburys" : "Sainsbury's Long Grain Rice 1kg"
    },
    "Penne Pasta" : {
        "tesco" : "Tesco Penne Pasta Quills 500G",
        "asda" : "ASDA Penne 500g",
        "aldi" : "Everyday Essentials Penne Pasta 500g",
        "waitrose" : "Essential Penne",
        "Sainsburys" : "Sainsbury's Quick Cook Penne Pasta 500g"
    },
    "WholeMeal Bread" : {
        "tesco" : "H.W. Nevill's Medium Sliced Wholemeal Bread 800g",
        "asda" : "The BAKERY at ASDA Wholemeal Medium Sliced Bread",
        "aldi" : "Everyday Essentials Medium Sliced Wholemeal Bread 800g",
        "waitrose" : "Hovis Wholemeal Medium Sliced Bread",
        "Sainsburys" : "Sainsbury's Medium Sliced Wholemeal Bread 800g"
    },
    "Olive Oil" : {
        "tesco" : "Tesco Extra Virgin Olive Oil 1Ltr",
        "asda" : "ASDA Extra Virgin Olive Oil",
        "aldi" : "Solesta Extra Virgin Olive Oil 1l",
        "waitrose" : "Waitrose Extra Virgin Olive Oil",
        "Sainsburys" : "Sainsbury's Olive Oil, Extra Virgin 1L"
    },
    "Eggs (6 pack)" : {
        "tesco" : "Tesco Large Free Range Eggs 6 Pack",
        "asda" : "ASDA 6 Large Free Range Eggs",
        "aldi" : "Merevale British Free Range Very Large Eggs 438g/6 Pack",
        "waitrose" : "Waitrose Blacktail Free Range Very Large Eggs",
        "Sainsburys" : "Sainsbury's British Free Range Eggs Large x6"
    },
    "Semi Skimmed Milk" : {
        "tesco" : "Tesco British Semi Skimmed Milk 1.13L, 2 Pints",
        "asda" : "ASDA British Milk Semi Skimmed 2 Pints",
        "aldi" : "Cowbelle British Semi-skimmed Milk 2 Pints",
        "waitrose" : "Essential British Free Range Semi-Skimmed Milk 2 Pints",
        "Sainsburys" : "Sainsbury's British Semi Skimmed Milk 1.13L (2 pint)"
    },
    "Granola" : {
        "tesco" : "Tesco Honey & Almond Granola 1Kg",
        "asda" : "ASDA Tropical Granola",
        "aldi" : "Harvest Morn Raisin & Almond Granola 1kg",
        "waitrose" : "Waitrose Raisin, Almond Honey Granola 1Kg",
        "Sainsburys" : "Sainsbury's Granola, Raisin, Nut & Honey 1kg"
    },
    "Salted Butter" : {
        "tesco" : "Tesco British Salted Block Butter 250G",
        "asda" : "ASDA British Salted Butter 250g",
        "aldi" : "Cowbelle British Salted Butter 250g",
        "waitrose" : "Essential Salted Butter",
        "Sainsburys" : "Sainsbury's British Butter, Salted 250g"
    },
    "Ketchup" : {
        "tesco" : "Tesco Tomato Ketchup 890G",
        "asda" : "ASDA Classic Tomato Ketchup 970g",
        "aldi" : "Bramwells Tomato Ketchup 550g/500ml",
        "waitrose" : "Essential Tomato Ketchup",
        "Sainsburys" : "Stamford Street Co. Tomato Ketchup 460g"
    },
    "Frozen French Fries" : {
        "tesco" : "Tesco French Fries 1.5Kg",
        "asda" : "ASDA French Fries",
        "aldi" : "Four Seasons Steak Cut Chips 1.5kg",
        "waitrose" : "Essential Frozen Straight Cut Oven Chips",
        "Sainsburys" : "Sainsbury's French Fries 1.5kg"
    },
    "Cheddar Cheese" : {
        "tesco" : "Tesco British Mature Cheddar Cheese 220G",
        "asda" : "ASDA Mature Cheddar Cheese",
        "aldi" : "Glen Lochy Lockerbie Mature Cheddar 200g",
        "waitrose" : "Essential Mature Cheddar Cheese Strength 4",
        "Sainsburys" : "Sainsbury's British Mature Cheddar Cheese 400g"
    },
    "Instant Coffee" : {
        "tesco" : "Tesco Gold Instant Coffee 200G",
        "asda" : "ASDA Gold Roasted Coffee Instant Granules 200g",
        "aldi" : "Alcafé Rich Roast Instant Coffee Granules 200g",
        "waitrose" : "Nescafe Gold Blend Instant Coffee",
        "Sainsburys" : "Kenco Smooth Instant Coffee 200g"
    },
    "Ground Beef" : {
        "tesco" : "Tesco Lean Beef Steak Mince 5% Fat 500g",
        "asda" : "ASDA Flavourful Lean Beef Steak Mince (Typically Less Than 5% Fat)",
        "aldi" : "Nature's Glen Scotch Beef Lean Mince 5% Fat 500g",
        "waitrose" : "Waitrose British Native Breed Beef Mince 5% Fat",
        "Sainsburys" : "Sainsbury's British or Irish 5% Fat Beef Mince 500g"
    }
}

# Check if df is stored in session state
if "df" in st.session_state:
    df = st.session_state.df
else:
    st.write("⚠️ No data available. Please visit the Data Analysis page first.")

st.title("📊 Supermarket Price Comparison Dashboard")

# Filter dataset for selected products
df_filtered = df[df["Name"].isin([name for products in product_mapping.values() for name in products.values()])]

# Get the latest prices for each selected product
df_filtered["Date"] = pd.to_datetime(df_filtered[["Year", "Month", "Day"]])
df_latest = df_filtered.sort_values("Date").groupby("Name").last().reset_index()

# Create 3 columns layout with 5 rows
total_products = len(product_mapping)
cols = st.columns(3)
row_count = 0

for product, stores in product_mapping.items():
    price_data = []
    cheapest_store = None
    cheapest_price = float('inf')
    cheapest_product = None

    for store, product_name in stores.items():
        product_row = df_latest[df_latest["Name"] == product_name]
        if not product_row.empty:
            price = product_row["Price"].values[0]
            price_data.append({"Store": store, "Price": price})

            if price < cheapest_price:
                cheapest_price = price
                cheapest_store = store
                cheapest_product = product_name

    # Ensure all five stores are represented, even if missing
    for store in ["Tesco", "Asda", "Aldi", "Waitrose", "Sainsbury's"]:
        if store not in [p["Store"] for p in price_data]:
            price_data.append({"Store": store, "Price": None})

    price_df = pd.DataFrame(price_data)
    
    fig = px.bar(
        price_df, x="Store", y="Price", text="Price",
        title=f"{product} Price Comparison",
        color="Store"
    )
    fig.update_traces(texttemplate="£%{text:.2f}", textposition="outside")
    fig.update_layout(yaxis_title="Price (£)", xaxis_title="Supermarket", height=500)

    with cols[row_count % 3]:
        with st.container():
            st.write(f"### {product}")
            st.write(f"**Cheapest Store:** {cheapest_store}")
            st.write(f"**Product Name:** {cheapest_product}")
            st.metric(
                label=f"**Price:**",
                value=f"£{cheapest_price:.2f}"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    row_count += 1

st.caption("Prices are based on the latest available scraped data.")