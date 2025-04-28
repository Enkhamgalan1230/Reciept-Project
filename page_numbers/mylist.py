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

    for tab, (month, entries) in zip(month_tabs, grouped_lists.items()):
        with tab:
            for entry in entries:
                timestamp = datetime.fromisoformat(entry["created_at"]).strftime("%d %B")

                with st.expander(f"Shopping List: ({timestamp})"):
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

                    # Prepare text content for download
                    txt_content = f"Shopping List ({timestamp})\n\n"
                    txt_content += "Items to Buy:\n"
                    if input_items:
                        for item in input_items:
                            txt_content += f"- {item.title()}\n"
                    else:
                        txt_content += "- No items available.\n"

                    txt_content += f"\nPotential Buys ({entry.get('store', 'Unknown Store')}):\n"
                    if matched_items:
                        for match in matched_items:
                            txt_content += f"- {match.get('Input', 'Unknown').title()} → {match.get('Matched Product', 'N/A')}\n"
                            txt_content += f"  Price: £{match.get('Price', 0.00):.2f}\n"
                            txt_content += f"  Discount: {'None' if match.get('Discount') in [None, 'NULL'] else match.get('Discount')}\n\n"
                    else:
                        txt_content += "- No matched items available.\n"

                    # Display on screen
                    st.markdown("### Shopping List")
                    if input_items:
                        for item in input_items:
                            st.markdown(f"- {item.title()}")
                    else:
                        st.markdown("_No items available._")

                    st.markdown(f"### Potential Buys ({entry.get('store', 'Unknown Store')})")
                    if matched_items:
                        for match in matched_items:
                            st.markdown(f"""
                            - **{match.get('Input', 'Unknown').title()}** → *{match.get('Matched Product', 'N/A')}*  
                            Price: £{match.get('Price', 0.00):.2f}  
                            Discount: {'None' if match.get('Discount') in [None, 'NULL'] else match.get('Discount')}
                            """)
                    else:
                        st.markdown("_No matched items available._")

                    # Properly format a very unique ID
                    created_at_full = entry["created_at"]  # e.g., 2025-04-22T09:25:00.123456

                    # Prepare a clean key
                    clean_created_at = created_at_full.replace(":", "-").replace(".", "-")
                    unique_key = f"download_button_{clean_created_at}_{entry.get('store', 'Unknown')}"

                    # Download button
                    st.download_button(
                        label="Download List(.txt)",
                        icon=":material/download:",
                        data=txt_content,
                        file_name=f"receipt_{timestamp.replace(' ', '_')}.txt",
                        mime="text/plain",
                        key=unique_key
                    )

                    # Unique delete key
                    delete_key = f"delete_button_{clean_created_at}_{entry.get('store', 'Unknown')}"

                    # Button to start delete confirmation
                    if st.button("Delete List", key=delete_key):
                        st.session_state[f"confirm_delete_{delete_key}"] = True

                    # If confirmation state is active
                    if st.session_state.get(f"confirm_delete_{delete_key}"):
                        
                        st.divider()
                        with st.container(border=True):
                            # Centered title
                            st.markdown("<h3 style='text-align: center;'>⚠️ Confirm Deletion</h3>", unsafe_allow_html=True)
                            # Centered caption
                            st.markdown("<p style='text-align: center;'>Are you sure you want to delete this shopping list? This action cannot be undone.</p>", unsafe_allow_html=True)

                            # Create 5 columns: [space] [Yes button] [small space] [No button] [space]
                            col1, col2, col3, col4 = st.columns([3, 0.7, 0.7, 3])

                            with col2:
                                if st.button("Yes, Delete", key=f"confirm_yes_{delete_key}"):
                                    try:
                                        supabase.table("shopping_lists").delete()\
                                            .eq("created_at", entry["created_at"])\
                                            .eq("user_email", user_email)\
                                            .execute()
                                        st.success("List deleted successfully.")
                                        st.session_state.pop(f"confirm_delete_{delete_key}", None)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed to delete list: {e}")

                            with col3:
                                if st.button("Nahh, Keep it", key=f"confirm_no_{delete_key}"):
                                    st.session_state.pop(f"confirm_delete_{delete_key}", None)