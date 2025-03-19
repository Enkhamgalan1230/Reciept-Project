import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time
import matplotlib.pyplot as plt
import plotly.express as px
import random

fun_facts = [
    # Tesco Fun Facts
    "Tesco introduced the Clubcard loyalty scheme in 1995! 🛒",
    "Tesco started as a market stall in London’s East End in 1919. 🏪",
    "Tesco operates in over 12 countries worldwide! 🌎",
    "Tesco’s first self-service store opened in 1948, inspired by the US supermarket model. 🏬",
    "Tesco was the first UK supermarket to sell petrol at its stores! ⛽",
    "In 2011, Tesco became the world's third-largest retailer by revenue. 💰",
    "Tesco has more than **4,000** stores across the UK! 🏢",
    "The Tesco Finest range was introduced in 1998 to offer premium products! 🥂",
    "Tesco’s **Fast Track checkout system** was one of the first self-service checkouts in the UK! 🔄",
    "Tesco started its **first online grocery delivery service** in 2000! 🚚",

    # Sainsbury's Fun Facts
    "Sainsbury's was founded in 1869 in London as a small dairy shop. 🏡",
    "Sainsbury's was the **first UK supermarket** to remove plastic bags for loose fruit and veg! 🌍",
    "Sainsbury’s is the second-largest supermarket chain in the UK! 🇬🇧",
    "In 1996, Sainsbury’s became the first UK supermarket to introduce self-checkouts! 🛍️",
    "The first Sainsbury's own-brand product was launched in 1882. 🏷️",
    "Sainsbury’s is known for its **‘Taste the Difference’ premium food range**! 🍽️",
    "Sainsbury's Nectar loyalty card launched in 2002 and is one of the UK's most popular! 💳",
    "Sainsbury’s was the first UK supermarket to **sell fair trade bananas** in 2000! 🍌",
    "Sainsbury’s was the **first retailer to ban energy drinks** for under-16s in 2018! 🚫",
    "Sainsbury’s is the **largest retailer of British organic produce** in the UK! 🥕",

    # Morrisons Fun Facts
    "Morrisons started as a **market stall in Bradford** in 1899. 🏪",
    "Morrisons is the **UK’s fourth-largest supermarket chain**. 🛒",
    "Morrisons was the **last of the 'Big Four' supermarkets** to introduce online shopping! 🖥️",
    "Morrisons owns **most of its food production facilities**, unlike other supermarkets! 🍽️",
    "Morrisons bought **Safeway** in 2004, doubling its number of stores! 🔄",
    "Morrisons introduced the UK’s first **paper bag scheme** to reduce plastic waste! 🌱",
    "Morrisons is famous for its **‘Market Street’ concept**, mimicking fresh food markets! 🍞",
    "Morrisons was the first UK supermarket to **sell only British fresh meat**. 🥩",
    "Morrisons **was founded as a butter and egg stall** before expanding to supermarkets! 🥚",
    "Morrisons is known for its **low-cost meal deals**, including the famous £3.50 lunch! 🥪",

    # Asda Fun Facts
    "Asda was founded in 1949 by a group of **Yorkshire dairy farmers**. 🥛",
    "Asda merged with Walmart in 1999, before splitting again in 2020. 🌎",
    "Asda was the **first UK supermarket** to introduce a drive-through grocery collection! 🚗",
    "Asda’s ‘Rollback’ campaign, launched in the 90s, became **iconic for price cuts**! 💷",
    "Asda is known for its **George clothing range**, introduced in 1989. 👕",
    "Asda was the first UK supermarket to offer **free child car seat fittings**! 🚼",
    "Asda has one of the **largest online grocery delivery networks** in the UK! 📦",
    "Asda's petrol stations **offer some of the cheapest fuel prices** in the UK! ⛽",
    "Asda was the **first UK retailer to introduce baby-changing rooms** in stores! 👶",
    "In 2022, Asda introduced a **budget-friendly 'Just Essentials' range** for lower costs! 🛍️",

    # Aldi Fun Facts
    "Aldi was founded in Germany in 1946 and expanded to the UK in 1990. 🇩🇪",
    "Aldi is famous for its **Super 6 deals**, offering discounts on fresh produce! 🍏",
    "Aldi is known for having **the world’s fastest checkout system**! 🚀",
    "Aldi’s private-label brands make up **more than 90% of its product range**! 🏷️",
    "Aldi sells over **20,000 bottles of Prosecco** every day in the UK! 🥂",
    "Aldi’s ‘Specialbuys’ aisle is famous for **unexpected bargains** like hot tubs! 🛁",
    "Aldi is the **UK’s cheapest supermarket** for basic groceries! 🛒",
    "Aldi was the **first UK supermarket to remove plastic trays from its fresh meat packs**! 🌍",
    "Aldi’s famous checkout speed is **three times faster** than rival supermarkets! ⏩",
    "Aldi operates a **no-frills shopping model** to keep costs low for customers! 💰"
]


def get_preloaded_fun_fact():
    return random.choice(fun_facts)

st.title("📊 Data")
st.markdown("---")

# Initialize Supabase connection
conn = st.connection("supabase", type=SupabaseConnection)

# Function to fetch data and cache it globally
# Only fetch data if it's not already stored in session state
if "df" not in st.session_state:
    @st.cache_data  # Cache the fetched data
    def fetch_data():
        try:
            # Step 1: Get total row count dynamically
            row_count_result = conn.table("Product").select("*", count="exact", head=True).execute()
            max_rows = row_count_result.count
            st.write(f"There are {max_rows} rows currently in the database.")

            # Show an initial fun message
            st.write("#### Loading fresh data from Supabase! 🍽️ Since we fetch 1,000 rows at a time, it may take a moment. Why not grab a coffee ☕ and enjoy a fun fact while you wait? ")

            # Step 2: Fetch data with pagination
            batch_size = 1000
            total_batches = (max_rows + batch_size - 1) // batch_size  # Round up

            # UI elements for updates
            progress_bar = st.progress(0)
            progress_text = st.empty()
            fun_fact_box = st.empty()  # Dynamic box for fun facts

            all_rows = []
            offset = 0

            for batch in range(1, total_batches + 1):
                try:
                    rows = conn.table("Product").select("*").range(offset, offset + batch_size - 1).execute()

                    if not rows.data:
                        break

                    all_rows.extend(rows.data)
                    offset += batch_size

                    # Update progress bar
                    progress_percentage = batch / total_batches
                    progress_bar.progress(min(progress_percentage, 1.0))

                    # Update progress text
                    progress_text.write(f"Fetching batch {batch}/{total_batches}...")

                    # Update fun fact every few batches
                    if batch % 5 == 0:  # Change the fun fact every 2 batches
                        fun_fact_box.success(f"🛒 **Did You Know?** {get_preloaded_fun_fact()}")

                    time.sleep(0.5)  # Rate limit

                except Exception as e:
                    st.write(f"Error at batch {batch}, offset {offset}: {e}")
                    break

            df = pd.DataFrame(all_rows)
            st.write("✅ Data fetching completed!.")
            st.balloons()
            return df

        except Exception as e:
            st.write(f"Error fetching data: {e}")
            return None

    df = fetch_data()
    st.session_state.df = df  # Store for later use
else:
    df = st.session_state.df  # Load cached data

if df is not None:
    st.write("✅ *Data loaded successfully! Nothing to see here.*")
else:
    st.write("⚠️ No data available.")