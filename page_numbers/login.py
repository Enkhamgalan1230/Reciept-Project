import streamlit as st
import bcrypt
from supabase import create_client, Client
import re
import random, smtplib
from email.message import EmailMessage
import traceback
from datetime import datetime

# ------------------- CONFIG -------------------
APP_NAME = "Receipt"
FROM_EMAIL = "zaecisama@gmail.com"
EMAIL = st.secrets["email"]["address"]
EMAIL_PASSWORD = st.secrets["email"]["password"]

SUPABASE_URL = "https://rgfhrhvdspwlexlymdga.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJnZmhyaHZkc3B3bGV4bHltZGdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEzODg2ODEsImV4cCI6MjA1Njk2NDY4MX0.P_hdynXVGULdvy-fKeBMkNAMsm83bK8v-027jyA6Ohs"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------- UTILITIES -------------------
def is_valid_password(pw):
    return (
        len(pw) >= 8 and
        not any(c.isspace() for c in pw) and
        re.search(r'[A-Z]', pw) and
        re.search(r'[0-9]', pw) and
        re.search(r'[!@#$%^&*(),.?":{}|<>]', pw)
    )

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_to_email(email):
    otp = generate_otp()
    st.session_state.generated_otp = otp
    msg = EmailMessage()
    msg.set_content(f"Thank you for using {APP_NAME}! Your verification code is: {otp}")
    msg["Subject"] = f"Your Signup Verification Code for {APP_NAME}"
    msg["From"] = FROM_EMAIL
    msg["To"] = email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# --- Init session key safely ---
if "supabase_user" not in st.session_state:
    st.session_state.supabase_user = None

st.markdown("## Account")

# ------------------- LOGGED IN VIEW -------------------
if st.session_state.supabase_user:
    user_email = st.session_state.supabase_user.user.email
    username_raw = user_email.split('@')[0]
    username_display = username_raw.capitalize()
    st.success(f"Welcome, {username_display}")

    if st.button("Log Out"):
        supabase.auth.sign_out()
        st.session_state.supabase_user = None

        # Optional: clear saved session data
        for key in ["essential_list", "voice_products", "secondary_list", "final_list_df", "selected_store"]:
            st.session_state.pop(key, None)

        st.rerun()

# ------------------- SIGN UP FLOW -------------------
else:
    auth_tab = st.pills("Choose an action", ["Log In", "Sign Up"], selection_mode="single", key="auth_mode")
    st.markdown("---")

    if auth_tab == "Sign Up":
        st.subheader("Create an Account")
        with st.form("signup_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Repeat Password", type="password")
            submit = st.form_submit_button("Verify Email")

            if submit:
                if password != confirm:
                    st.error("Passwords do not match.")
                elif not is_valid_password(password):
                    st.error("Password must be 8+ chars, include a capital letter, number, and special character.")
                else:
                    send_otp_to_email(email)
                    st.session_state.temp_signup = {"email": email, "password": password}
                    st.success("Verification code sent. Please check your email.")

    if "temp_signup" in st.session_state:
        st.markdown("### Enter the verification code")
        otp_input = st.text_input("Verification Code", max_chars=6)
        verify_btn = st.button("Create Account")

        if verify_btn:
            if otp_input == st.session_state.generated_otp:
                try:
                    email = st.session_state.temp_signup["email"]
                    password = st.session_state.temp_signup["password"]
                    res = supabase.auth.sign_up({"email": email, "password": password})
                    if res.user:
                        login = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        st.session_state.supabase_user = login
                        st.success("Account created and you're now logged in!")

                        del st.session_state.temp_signup
                        del st.session_state.generated_otp
                        st.rerun()
                    else:
                        st.error("Signup failed. Please try again.")
                except Exception as e:
                    st.error("Signup error.")
                    st.text(str(e))
            else:
                st.error("Incorrect verification code.")

    if auth_tab == "Log In":
        st.subheader("Log In")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")

        if st.button("Log In"):
            try:
                res = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                if res.user:
                    st.session_state.supabase_user = res
                    st.success("Login successful.")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
            except Exception as e:
                st.error("Login failed.")
                st.text(str(e))