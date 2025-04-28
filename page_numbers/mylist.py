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
st.title("🧾 My Shopping Lists")

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
    grouped_lists = defaultdict(list)
    for entry in lists:
        month_year = datetime.fromisoformat(entry["created_at"]).strftime("%B %Y")
        grouped_lists[month_year].append(entry)

    month_tabs = st.tabs(list(grouped_lists.keys()))

    for tab, (month, entries) in zip(month_tabs, grouped_lists.items()):
        with tab:
            for entry in entries:
                timestamp = datetime.fromisoformat(entry["created_at"]).strftime("%d %B %Y - %I:%M %p")

                with st.popover(f"🧾 {timestamp}"):
                    # Parse input_items
                    try:
                        input_items = json.loads(entry.get("input_items", "[]"))
                    except:
                        input_items = entry.get("input_items", [])

                    # Parse matched_items
                    try:
                        matched_items = json.loads(entry.get("matched_items", "[]"))
                    except:
                        matched_items = entry.get("matched_items", [])

                    # Build receipt
                    receipt = f"""
<div style="font-family: 'Courier New', monospace; background-color: white; padding: 20px; border: 2px dashed grey; width: 300px; margin: auto; color: black;">
    <h4 style="text-align: center;">RECEIPT</h4>
    <p style="text-align: center; font-size: 12px;">{timestamp}</p>
    <hr>

    <strong>🛒 Shopping List:</strong><br>
    {"<br>".join(f"- {item}" for item in input_items)}<br><br>

    <strong>🛍️ Potential Buys ({entry.get('store', 'Unknown Store')}):</strong><br>
    {"<br>".join(
        f"{match.get('Input', 'Unknown')} -> {match.get('Matched Product', 'N/A')}<br>"
        f"Price: £{match.get('Price', 0.00):.2f} | "
        f"Discount: {'None' if match.get('Discount') in [None, 'NULL'] else match.get('Discount')}"
        for match in matched_items
    )}
    <hr>
    <p style="text-align: center;">Thank you for using SmartCart!</p>
</div>
                    """

                    st.markdown(receipt, unsafe_allow_html=True)