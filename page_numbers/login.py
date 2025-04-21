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

# ------------------- SESSION INIT -------------------
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

st.markdown("## 👤 Account")
auth_tab = st.pills("Choose an action", ["Log In", "Sign Up"], selection_mode="single")
st.markdown("---")

# ------------------- LOGGED IN VIEW -------------------
if st.session_state.logged_in_user:
    st.success(f"Welcome, {st.session_state.logged_in_user}")
    if st.button("Log Out"):
        st.session_state.logged_in_user = None
        st.session_state.generated_otp = None
        st.session_state.temp_signup = None

# ------------------- SIGN UP FLOW -------------------
elif auth_tab == "Sign Up":
    with st.container():
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
        with st.container():
            otp_input = st.text_input("Verification Code")
            verify_btn = st.button("Create Account")

            if verify_btn:
                if otp_input == st.session_state.generated_otp:
                    hashed_pw = hash_password(st.session_state.temp_signup["password"])
                    email = st.session_state.temp_signup["email"]
                    user_data = {
                        "username": email,
                        "password_hash": hashed_pw,
                        "created_at": datetime.utcnow().isoformat()
                    }
                    try:
                        existing = supabase.table("users").select("id").eq("username", email).execute()
                        if existing.data:
                            st.error("This email is already registered.")
                        else:
                            supabase.table("users").insert(user_data).execute()
                            st.success("Account created successfully!")
                            st.session_state.logged_in_user = email
                            del st.session_state.temp_signup
                            del st.session_state.generated_otp
                    except Exception as e:
                        st.error("Signup failed.")
                        st.text(traceback.format_exc())
                else:
                    st.error("Invalid verification code.")

# ------------------- LOGIN FLOW -------------------
elif auth_tab == "Log In":
    with st.container():
        st.subheader("Log In")
        with st.form("login_form"):
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_pw")
            login_submit = st.form_submit_button("Log In")

            if login_submit:
                try:
                    result = supabase.table("users").select("*").eq("username", login_email).execute()
                    if not result.data:
                        st.error("No account found with this email.")
                    else:
                        user = result.data[0]
                        stored_hash = user["password_hash"]
                        if bcrypt.checkpw(login_password.encode(), stored_hash.encode()):
                            st.success("Login successful.")
                            st.session_state.logged_in_user = login_email
                        else:
                            st.error("Incorrect password.")
                except Exception:
                    st.error("Login failed.")
                    st.text(traceback.format_exc())