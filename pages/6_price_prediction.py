import streamlit as st
import streamlit as st

st.title("Price Prediction")


# Check if df is stored in session state
if "df" in st.session_state:
    df = st.session_state.df  # Retrieve stored data
    st.write("Nothing here yet!")
else:
    st.write("⚠️ No data available. Please visit the Data Analysis page first.")