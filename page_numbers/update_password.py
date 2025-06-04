import streamlit as st
from supabase import create_client, Client
import supabase
from urllib.parse import urlparse, parse_qs
from page_numbers.login import is_valid_password
import streamlit.components.v1 as components

SUPABASE_URL = "https://rgfhrhvdspwlexlymdga.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJnZmhyaHZkc3B3bGV4bHltZGdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEzODg2ODEsImV4cCI6MjA1Njk2NDY4MX0.P_hdynXVGULdvy-fKeBMkNAMsm83bK8v-027jyA6Ohs"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.subheader("Reset Your Password")

components.html(
    """
    <script>
        const hashParams = new URLSearchParams(window.location.hash.slice(1));
        const access_token = hashParams.get("access_token");
        const type = hashParams.get("type");

        if (access_token && type) {
            const newUrl = `${window.location.pathname}?access_token=${access_token}&type=${type}`;
            if (!window.location.search.includes("access_token")) {
                window.location.replace(newUrl);
            }
        }
    </script>
    """,
    height=0,
)

# --- Step 1: Extract token from query string ---
params = st.query_params()
access_token = params.get("access_token", [None])[0]
recovery_type = params.get("type", [None])[0]

# --- Step 2: Verify token and create session ---
if recovery_type == "recovery" and access_token and "supabase_user" not in st.session_state:
    try:
        session = supabase.auth.verify_otp({
            "type": "recovery",
            "token": access_token
        })
        st.session_state.supabase_user = session
        st.success("Recovery session started. You may now reset your password.")
    except Exception as e:
        st.error("Token verification failed.")
        st.text(str(e))
        st.stop()

# --- Step 3: Password reset form ---
new_pw = st.text_input("New Password", type="password")
confirm_pw = st.text_input("Confirm Password", type="password")
submit_pw = st.button("Update Password")

if submit_pw:
    if new_pw != confirm_pw:
        st.error("Passwords do not match.")
    elif not is_valid_password(new_pw):
        st.error("Password must be 8+ chars with uppercase, number, special char.")
    elif "supabase_user" not in st.session_state:
        st.error("Auth session missing! Please use the link from your email again.")
    else:
        try:
            supabase.auth.update_user({"password": new_pw})
            st.success("Password successfully updated. You may now log in.")
        except Exception as e:
            st.error("Failed to update password.")
            st.text(str(e))