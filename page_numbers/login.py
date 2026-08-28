import re

import streamlit as st

from local_store import authenticate, create_user


def is_valid_password(password):
    return (
        len(password) >= 8
        and not any(char.isspace() for char in password)
        and re.search(r"[A-Z]", password)
        and re.search(r"[0-9]", password)
        and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )


if "local_user" not in st.session_state:
    st.session_state.local_user = None

st.markdown("## Account")

if st.session_state.local_user:
    email = st.session_state.local_user["email"]
    st.success(f"Welcome, {email.split('@')[0].capitalize()}")
    if st.button("Log Out"):
        st.session_state.local_user = None
        for key in ["essential_list", "voice_products", "secondary_list", "final_list_df", "selected_store"]:
            st.session_state.pop(key, None)
        st.rerun()
else:
    auth_tab = st.pills("Choose an action", ["Log In", "Sign Up"], selection_mode="single", key="auth_mode")
    st.markdown("---")

    if auth_tab == "Sign Up":
        st.subheader("Create an Account")
        with st.form("signup_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Repeat Password", type="password")
            submit = st.form_submit_button("Create Account")
        if submit:
            if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
                st.error("Please enter a valid email address.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif not is_valid_password(password):
                st.error("Password must be 8+ chars, include a capital letter, number, and special character.")
            else:
                created, message = create_user(email, password)
                if created:
                    st.session_state.local_user = {"email": email.strip().lower()}
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    elif auth_tab == "Log In":
        st.subheader("Log In")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.button("Log In"):
            user = authenticate(email, password)
            if user:
                st.session_state.local_user = user
                st.success("Login successful.")
                st.rerun()
            else:
                st.error("Invalid email or password.")
