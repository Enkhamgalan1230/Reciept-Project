import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time
import matplotlib.pyplot as plt
import plotly.express as px
from fuzzywuzzy import process


product_mapping = {
    "Chicken Breast (1kg)" : {
        "tesco" : "Tesco British Chicken Breast Fillets 950G",
        "asda" : "ASDA Tender Chicken Breast Fillets",
        "aldi" : "Shazans Chicken Breast Fillets 950g",
        "waitrose" : "Essential Chicken Breast Fillets",
        "Sainsburys" : "Sainsburys British Fresh Chicken Breast Fillets Skinless & Boneless 1kg"
    },
    "Canned Tuna (~145g)" : {
        "tesco" : "Stockwell & Co Tuna Chunks In Brine 145G",
        "asda" : "ASDA Skipjack Tuna Chunks in Brine",
        "aldi" : "Everyday Essentials Tuna Chunks In Brine 145g",
        "waitrose" : "Essential MSC Tuna Chunks in Brine",
        "Sainsburys" : "Sainsbury's Tuna Chunks in Brine 145g"
    },
    "Long Grain Rice (1kg)" : {
        "tesco" : "Tesco Easy Cook Long Grain Rice 1Kg",
        "asda" : "ASDA Long Grain White Rice 1kg",
        "aldi" : "Worldwide Foods Easy Cook Long Grain Rice 1kg",
        "waitrose" : "Essential Long Grain Rice Easy Cook",
        "Sainsburys" : "Sainsbury's Long Grain Rice 1kg"
    },
    "Penne Pasta (500g)" : {
        "tesco" : "Tesco Penne Pasta Quills 500G",
        "asda" : "ASDA Penne 500g",
        "aldi" : "Everyday Essentials Penne Pasta 500g",
        "waitrose" : "Essential Penne",
        "Sainsburys" : "Sainsbury's Quick Cook Penne Pasta 500g"
    },
    "WholeMeal Bread (800g)" : {
        "tesco" : "H.W. Nevills Medium Sliced Wholemeal Bread 800g",
        "asda" : "The BAKERY at ASDA Wholemeal Medium Sliced Bread",
        "aldi" : "Everyday Essentials Medium Sliced Wholemeal Bread 800g",
        "waitrose" : "Hovis Wholemeal Medium Sliced Bread",
        "Sainsburys" : "Sainsbury's Medium Sliced Wholemeal Bread 800g"
    },
    "Olive Oil (1l)" : {
        "tesco" : "Tesco Extra Virgin Olive Oil 1Ltr",
        "asda" : "ASDA Extra Virgin Olive Oil",
        "aldi" : "Solesta Extra Virgin Olive Oil 1l",
        "waitrose" : "Waitrose Extra Virgin Olive Oil",
        "Sainsburys" : "Sainsbury's Olive Oil, Extra Virgin 1L"
    },
    "Eggs (6pc)" : {
        "tesco" : "Tesco Large Free Range Eggs 6 Pack",
        "asda" : "ASDA 6 Large Free Range Eggs",
        "aldi" : "Merevale British Free Range Very Large Eggs 438g/6 Pack",
        "waitrose" : "Waitrose Blacktail Free Range Very Large Eggs",
        "Sainsburys" : "Sainsbury's British Free Range Eggs Large x6"
    },
    "Semi Skimmed Milk (2pints)" : {
        "tesco" : "Tesco British Semi Skimmed Milk 1.13L, 2 Pints",
        "asda" : "ASDA British Milk Semi Skimmed 2 Pints",
        "aldi" : "Cowbelle British Semi-skimmed Milk 2 Pints",
        "waitrose" : "Essential British Free Range Semi-Skimmed Milk 2 Pints",
        "Sainsburys" : "Sainsbury British Semi Skimmed Milk 1.13L"
    },
    "Granola (1kg)" : {
        "tesco" : "Tesco Honey & Almond Granola 1Kg",
        "asda" : "ASDA Tropical Granola",
        "aldi" : "Harvest Morn Raisin & Almond Granola 1kg",
        "waitrose" : "Waitrose Raisin, Almond Honey Granola 1Kg",
        "Sainsburys" : "Sainsbury's Granola, Raisin, Nut & Honey 1kg"
    },
    "Salted Butter(250g)" : {
        "tesco" : "Tesco British Salted Block Butter 250G",
        "asda" : "ASDA British Salted Butter 250g",
        "aldi" : "Cowbelle British Salted Butter 250g",
        "waitrose" : "Essential Salted Butter",
        "Sainsburys" : "Sainsbury's British Butter, Salted 250g"
    },
    "Ketchup(460g-970g)" : {
        "tesco" : "Tesco Tomato Ketchup 890G",
        "asda" : "ASDA Classic Tomato Ketchup 970g",
        "aldi" : "Bramwells Tomato Ketchup 550g/500ml",
        "waitrose" : "Essential Tomato Ketchup",
        "Sainsburys" : "Stamford Street Co. Tomato Ketchup 460g"
    },
    "Frozen French Fries(~1.5kg)" : {
        "tesco" : "Tesco French Fries 1.5Kg",
        "asda" : "ASDA French Fries",
        "aldi" : "Four Seasons Steak Cut Chips 1.5kg",
        "waitrose" : "Essential Frozen Straight Cut Oven Chips",
        "Sainsburys" : "Sainsbury's French Fries 1.5kg"
    },
    "Cheddar Cheese(~200g)" : {
        "tesco" : "Tesco British Mature Cheddar Cheese 220G",
        "asda" : "ASDA Mature Cheddar Cheese",
        "aldi" : "Glen Lochy Lockerbie Mature Cheddar 200g",
        "waitrose" : "Essential Mature Cheddar Cheese Strength 4",
        "Sainsburys" : "Sainsbury's British Mature Cheddar Cheese 400g"
    },
    "Instant Coffee(200g)" : {
        "tesco" : "Tesco Gold Instant Coffee 200G",
        "asda" : "ASDA Gold Roasted Coffee Instant Granules 200g",
        "aldi" : "Alcafé Rich Roast Instant Coffee Granules 200g",
        "waitrose" : "Nescafe Gold Blend Instant Coffee",
        "Sainsburys" : "Kenco Smooth Instant Coffee 200g"
    },
    "Ground Beef(500g)" : {
        "tesco" : "Tesco Lean Beef Steak Mince 5% Fat 500g",
        "asda" : "ASDA Flavourful Lean Beef Steak Mince",
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

st.title("📊 Price Comparison")
st.markdown("---")

st.subheader("🏆 Dashboard with 15 Popular Items")

# Filter dataset for selected products
df_filtered = df[df["Name"].isin([name for products in product_mapping.values() for name in products.values()])]

# Get the latest prices for each selected product
df_filtered["Date"] = pd.to_datetime(df_filtered[["Year", "Month", "Day"]])
df_latest = df_filtered.sort_values("Date").groupby("Name").last().reset_index()

# Create 4 columns layout
total_products = len(product_mapping)
cols = st.columns(4)
row_count = 0

for product, stores in product_mapping.items():
    price_data = []
    cheapest_store = None
    cheapest_price = float('inf')
    cheapest_product = None

    for store, product_name in stores.items():
        product_row = df_latest[df_latest["Name"].str.contains(product_name, case=False, na=False)]
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
    price_df.dropna(subset=["Price"], inplace=True)  # Remove empty prices to prevent blank charts
    
    if not price_df.empty:
        fig = px.bar(
            price_df, x="Store", y="Price", text="Price",
            color="Store"
        )
        fig.update_traces(texttemplate="£%{text:.2f}", textposition="outside")
        fig.update_layout(
            yaxis_title="Price (£)",
            xaxis_title="Supermarket",
            height=300,
            xaxis_tickangle=-45  # Rotate x-axis labels to -45 degrees
            xaxis=dict(showticklabels=False)
        )

        with cols[row_count % 4]:
            with st.container(border=True, height=300):  # Fixed height for alignment
                st.markdown(f"#### 🛒 {product}")
                st.markdown(f"**Cheapest Store:** `{cheapest_store.capitalize()}`")
                st.markdown(f"**Product Name:** `{cheapest_product}`")
                st.metric(
                    label=f"✅ **Price:**",
                    value=f"£{cheapest_price:.2f}"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    row_count += 1

st.caption("📌 Prices are based on the latest available scraped data.")

st.markdown("---")

st.subheader("🔍 Search Comparison")

# Convert date columns into a single Date column
df["Date"] = pd.to_datetime(df[["Year", "Month", "Day"]])

# Keep only the latest data per product
df_latest = df.sort_values("Date").groupby("Name").last().reset_index()

# Create a new column 'Unit' that consolidates unit information
def determine_unit(row):
    if row["Unit_each"] > 0:
        return "each"
    elif row["Unit_kg"] > 0:
        return "kg"
    elif row["Unit_litre"] > 0:
        return "litre"
    return "N/A"

df_latest["Unit"] = df_latest.apply(determine_unit, axis=1)

# Drop unnecessary columns
df_latest = df_latest.drop(columns=["Year", "Month", "Day", "Unit_each", "Unit_kg", "Unit_litre", "Date"])

# Load subcategories from CSV
file_path = "subcategory.csv"
subcategories_df = pd.read_csv(file_path)
subcategory_list = subcategories_df["Subcategory"].unique().tolist()

# Allow multiple subcategory selections using st.pills with selection_mode="multi"
with st.container(border=True, height=180):
    selected_subcategories = st.pills("Choose product subcategories:", subcategory_list, selection_mode="multi")

# Filter data based on selected subcategories
if selected_subcategories:
    df_filtered = df_latest[df_latest["Subcategory"].isin(selected_subcategories)]
else:
    df_filtered = df_latest  # If nothing is selected, show all data

# User input for keyword
keyword = st.text_input("Enter a product name", placeholder="Ex: Chicken breast 400g")

def find_strict_match_products(df, keyword):
    """ Returns products that contain all keywords in the input query """
    keywords = keyword.lower().split()  # Split input into words
    df["match_score"] = df["Name"].apply(
        lambda x: sum(kw in x.lower() for kw in keywords)  # Count how many keywords match
    )
    return df[df["match_score"] == len(keywords)].drop(columns=["match_score"])  # Keep only full matches

if keyword:
    filtered_df = find_strict_match_products(df_filtered, keyword)

    # Ensure "Unit" exists in the filtered data
    if "Unit" not in filtered_df.columns:
        st.write("⚠️ 'Unit' column is missing from the filtered data. Displaying available columns.")
        st.dataframe(filtered_df)
    else:
        # Display results in ascending order of price
        filtered_df = filtered_df.sort_values(by="Price", ascending=True)

        # Display table with horizontal scroll and limit height
        st.dataframe(
            filtered_df[["Store_Name", "Price", "Discount price", "Subcategory", "Name", "Standardised price per unit", "Unit", "Category"]],
            height=400
        )