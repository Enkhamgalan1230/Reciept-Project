import streamlit as st
from supabase import create_client, Client
import supabase
from urllib.parse import urlparse, parse_qs
from page_numbers.login import is_valid_password
import streamlit.components.v1 as components
import time


SUPABASE_URL = "https://rgfhrhvdspwlexlymdga.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJnZmhyaHZkc3B3bGV4bHltZGdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEzODg2ODEsImV4cCI6MjA1Njk2NDY4MX0.P_hdynXVGULdvy-fKeBMkNAMsm83bK8v-027jyA6Ohs"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.subheader("Reset Your Password")
st.warning("Currently working on this feature! Sorry")

components.html(
    """
    <script>
        const hashParams = new URLSearchParams(window.location.hash.slice(1));
        const access_token = hashParams.get("access_token");
        const refresh_token = hashParams.get("refresh_token");
        const type = hashParams.get("type");

        const alreadyReloaded = window.location.href.includes("reload=true");

        if (access_token && type && !alreadyReloaded) {
            const baseUrl = window.location.href.split('#')[0];
            const newUrl = `${baseUrl}?access_token=${access_token}&refresh_token=${refresh_token}&type=${type}&reload=true`;
            window.location.replace(newUrl);
        }
    </script>
    """,
    height=0,
)


time.sleep(1)

params = st.query_params

if not params.get("access_token"):
    st.warning("Waiting for secure session to load... (JavaScript redirect in progress)")
    st.stop()
    
access_token = params.get("access_token", [None])[0]
refresh_token = params.get("refresh_token", [None])[0]
recovery_type = params.get("type", [None])[0]

st.write("Access Token:", access_token)
st.write("Refresh Token:", refresh_token)
st.write("Recovery Type:", recovery_type)
# Store in session for later
st.session_state.access_token = access_token
st.session_state.refresh_token = refresh_token

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
    elif not (st.session_state.get("access_token") or access_token):
        st.error("Auth token missing! Please refresh the page or use the reset link again.")
    else:
        try:
            # Set session using access token (even though refresh token is missing)
            supabase.auth.set_session(
                st.session_state.get("access_token") or access_token,
                st.session_state.get("refresh_token") or refresh_token
            )

            # Now update password
            supabase.auth.update_user({"password": new_pw})

            st.success("Password successfully updated. You may now log in.")
        except Exception as e:
            st.error("Failed to update password.")
            st.text(str(e))