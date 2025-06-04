import streamlit as st
from supabase import create_client, Client
import supabase
from page_numbers.login import is_valid_password

SUPABASE_URL = "https://rgfhrhvdspwlexlymdga.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJnZmhyaHZkc3B3bGV4bHltZGdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEzODg2ODEsImV4cCI6MjA1Njk2NDY4MX0.P_hdynXVGULdvy-fKeBMkNAMsm83bK8v-027jyA6Ohs"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.subheader("Reset Your Password")

params = st.query_params
access_token = params.get("access_token")
recovery_type = params.get("type")

if recovery_type == "recovery" and access_token:
    try:
        session = supabase.auth.verify_otp({
            "type": "recovery",
            "token": access_token
        })
        st.session_state.supabase_user = session
    except Exception as e:
        st.error("Failed to verify token.")
        st.stop()

# --- UI ---
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
            st.success("Password updated successfully. You can now log in.")
        except Exception as e:
            st.error("Failed to update password.")
            st.text(str(e))