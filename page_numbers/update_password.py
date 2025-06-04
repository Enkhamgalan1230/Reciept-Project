import streamlit as st
from supabase import create_client, Client
import supabase
from page_numbers.login import is_valid_password

st.subheader("Reset Your Password")

new_pw = st.text_input("New Password", type="password")
confirm_pw = st.text_input("Confirm Password", type="password")
submit_pw = st.button("Update Password")

if submit_pw:
    if new_pw != confirm_pw:
        st.error("Passwords do not match.")
    elif not is_valid_password(new_pw):
        st.error("Weak password.")
    else:
        try:
            supabase.auth.update_user({"password": new_pw})
            st.success("Password updated successfully.")
            st.experimental_rerun()
        except Exception as e:
            st.error("Failed to update password.")
            st.text(str(e))