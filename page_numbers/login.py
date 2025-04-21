import streamlit as st
import bcrypt
from supabase import create_client, Client
import re
import random, smtplib
from email.message import EmailMessage


url = "https://rgfhrhvdspwlexlymdga.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJnZmhyaHZkc3B3bGV4bHltZGdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEzODg2ODEsImV4cCI6MjA1Njk2NDY4MX0.P_hdynXVGULdvy-fKeBMkNAMsm83bK8v-027jyA6Ohs"

supabase = create_client(url, key)

if "show_signup_form" not in st.session_state:
    st.session_state.show_signup_form = False

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
    msg.set_content(f"Your verification code is: {otp}")
    msg["Subject"] = "Your Signup Verification Code"
    msg["From"] = "your@email.com"
    msg["To"] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("your@email.com", "your-app-password")
        server.send_message(msg)
    st.success("Verification code sent to your email!")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


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
            # Hash & store
            hashed_pw = hash_password(st.session_state.temp_signup["password"])
            supabase.table("users").insert({
                "username": st.session_state.temp_signup["email"],
                "password_hash": hashed_pw
            }).execute()
            st.success("Account created successfully!")
            st.session_state.logged_in_user = st.session_state.temp_signup["email"]
            del st.session_state.temp_signup
            del st.session_state.generated_otp
        else:
            st.error("Invalid verification code.")