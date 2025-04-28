import streamlit as st 
from supabase import create_client, Client
from datetime import datetime
import os
import json
from collections import defaultdict

# --- Supabase Setup ---

SUPABASE_URL = "https://rgfhrhvdspwlexlymdga.supabase.co"
SUPABASE_KEY = st.secrets["SUPABASE_SERVICE"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Session check ---
if "supabase_user" not in st.session_state:
    st.session_state.supabase_user = None

# --- Authenticated view ---
if st.session_state.supabase_user:
    user_email = st.session_state.supabase_user.user.email
    username_raw = user_email.split('@')[0]
    username_display = username_raw.capitalize()
    st.success(f"Welcome, {username_display}")
else:
    st.error("🔐 You must be logged in to view your saved lists.")
    st.stop()

# --- Page Title ---
st.title(" My Shopping Lists")

# --- Fetch user's shopping lists ---
with st.spinner("Loading your saved lists..."):

    response = supabase.table("shopping_lists")\
        .select("*")\
        .eq("user_email", user_email.lower())\
        .order("created_at", desc=True)\
        .execute()

    lists = response.data

# --- Display lists grouped by month ---
if not lists:
    st.info("No shopping lists found.")
else:
    # Group lists by Month-Year
    grouped_lists = defaultdict(list)
    for entry in lists:
        month_year = datetime.fromisoformat(entry["created_at"]).strftime("%B %Y")  # e.g., "April 2025"
        grouped_lists[month_year].append(entry)

    # Create tabs for each month
    month_tabs = st.tabs(list(grouped_lists.keys()))

    # Inside each tab
    for tab, (month, entries) in zip(month_tabs, grouped_lists.items()):
        with tab:
            for entry in entries:
                timestamp = datetime.fromisoformat(entry["created_at"]).strftime("%d %B %Y - %I:%M %p")

                with st.popover(f"🛒 {timestamp}"):
                    # 📝 Parse input_items
                    try:
                        input_items = json.loads(entry.get("input_items", "[]"))
                    except:
                        input_items = entry.get("input_items", [])

                    st.markdown("### 📝 Shopping List")
                    st.write(", ".join(input_items) if input_items else "_None_")

                    # 🛍️ Parse matched_items
                    try:
                        matched_items = json.loads(entry.get("matched_items", "[]"))
                    except:
                        matched_items = entry.get("matched_items", [])

                    st.markdown(f"### 🛍️ Potential Buys ({entry.get('store', 'Unknown Store')})")

                    if matched_items:
                        for match in matched_items:
                            st.markdown(f"""
                            - **{match.get('Input', 'Unknown')}** → *{match.get('Matched Product', 'N/A')}*  
                              Price: £{match.get('Price', 0.00):.2f}  
                              Discount: {'None' if match.get('Discount') in [None, 'NULL'] else match.get('Discount')}
                            """)
                    else:
                        st.markdown("_No matched items available._")