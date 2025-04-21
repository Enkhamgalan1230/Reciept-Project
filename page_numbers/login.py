import streamlit as st
import bcrypt
from supabase import create_client, Client
import re
import random, smtplib
from email.message import EmailMessage
import traceback
from datetime import datetime

EMAIL = st.secrets["email"]["address"]
EMAIL_PASSWORD = st.secrets["email"]["password"]

url = "https://rgfhrhvdspwlexlymdga.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJnZmhyaHZkc3B3bGV4bHltZGdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEzODg2ODEsImV4cCI6MjA1Njk2NDY4MX0.P_hdynXVGULdvy-fKeBMkNAMsm83bK8v-027jyA6Ohs"

supabase = create_client(url, key)

if "show_signup_form" not in st.session_state:
    st.session_state.show_signup_form = False

if "show_login_form" not in st.session_state:
    st.session_state.show_login_form = False

if st.button("Log In"):
    st.session_state.show_login_form = True

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
    msg.set_content(f"Thank you for using Receipt! Your verification code is: {otp}")
    msg["Subject"] = "Your Signup Verification Code for Receipt"
    msg["From"] = "zaecisama@gmail.com"
    msg["To"] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

col1, col2 = st.columns(2)


if "logged_in_user" in st.session_state:
    st.success(f"Welcome, {st.session_state.logged_in_user}")
    if st.button("Log Out"):
        del st.session_state.logged_in_user
        st.session_state.show_signup_form = False
        st.session_state.show_login_form = False
else:
    with col1:
        st.subheader("Sign Up")
        # Your existing signup code here

        if st.button("Sign Up"):
            st.session_state.show_signup_form = True

        if st.session_state.show_signup_form:
            with st.form("signup_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                confirm = st.text_input("Confirm Password", type="password")
                submit = st.form_submit_button("Send Verification Code")

                if submit:
                    if password != confirm:
                        st.error("Passwords do not match.")
                    elif not is_valid_password(password):
                        st.error("Password must have no spaces, 1 uppercase letter, 1 number, 1 special char, and be 8+ chars.")
                    else:
                        send_otp_to_email(email)
                        st.session_state.temp_signup = {
                            "email": email,
                            "password": password
                        }

        if "temp_signup" in st.session_state:
            otp_input = st.text_input("Enter the verification code sent to your email")
            verify_btn = st.button("Verify & Create Account")

            if verify_btn:
                if otp_input == st.session_state.generated_otp:
                    # Hash password
                    hashed_pw = hash_password(st.session_state.temp_signup["password"])
                    email = st.session_state.temp_signup["email"]

                    user_data = {
                        "username": email,
                        "password_hash": hashed_pw,  # Only needed if not default
                        "created_at": datetime.utcnow().isoformat()
                    }

                    try:
                        existing = supabase.table("users").select("id").eq("username", email).execute()
                        if existing.data:
                            st.error("Email already registered. Try logging in.")
                        else:
                            res = supabase.table("users").insert(user_data).execute()
                        st.success("Account created successfully!")
                        st.session_state.logged_in_user = email
                        del st.session_state.temp_signup
                        del st.session_state.generated_otp
                    except Exception as e:
                        st.error("Insert failed!")
                        st.text("Error details: Show to Entwan")
                        st.text(traceback.format_exc())
                else:
                    st.error("Invalid verification code.")

    with col2:
        if st.session_state.show_login_form:
            with st.form("login_form"):
                st.subheader("Log In")
                login_email = st.text_input("Email", key="login_email")
                login_password = st.text_input("Password", type="password", key="login_pw")
                login_submit = st.form_submit_button("Log In")

                if login_submit:
                    try:
                        result = supabase.table("users").select("*").eq("username", login_email).execute()

                        if not result.data:
                            st.error("No account found with that email.")
                        else:
                            user = result.data[0]
                            stored_hash = user["password_hash"]

                            if bcrypt.checkpw(login_password.encode(), stored_hash.encode()):
                                st.success("Login successful.")
                                st.session_state.logged_in_user = login_email
                                st.session_state.show_login_form = False  # Hide form after success
                            else:
                                st.error("Incorrect password.")
                    except Exception as e:
                        st.error("Login failed.")