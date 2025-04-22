import streamlit as st 
from supabase import create_client, Client
from datetime import datetime
import os

# --- Supabase Setup ---

SUPABASE_URL = st.secrets["connections.supabase"]["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["connections.supabase"]["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- Session check ---
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# --- Welcome message ---
if st.session_state.logged_in_user:
    username_raw = st.session_state.logged_in_user.split('@')[0]
    username_display = username_raw.capitalize()
    st.success(f"Welcome, {username_display}")
else:
    st.error("You must be logged in to view your saved lists.")
    st.stop()

# --- Page Title ---
st.title("📂 My Shopping Lists")

# --- Fetch user's shopping lists ---
with st.spinner("Loading your saved lists..."):
    response = supabase.table("shopping_lists")\
        .select("*")\
        .eq("user_email", st.session_state.logged_in_user)\
        .order("timestamp", desc=True)\
        .execute()

    lists = response.data

# --- Display lists ---
if not lists:
    st.info("No shopping lists found.")
else:
    for i, entry in enumerate(lists):
        st.markdown("---")

        # Timestamp
        timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%d %B %Y - %I:%M %p")
        st.subheader(f"🕒 {timestamp}")

        # Input Items
        st.markdown("### 📝 Shopping List")
        input_items = entry.get("input_items", [])
        st.write(", ".join(input_items) if input_items else "_None_")

        # Matched Items
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