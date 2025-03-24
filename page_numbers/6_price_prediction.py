import streamlit as st
import streamlit as st

st.title("Price Prediction", anchor=False)


# Check if df is stored in session state
if "df" in st.session_state:
    df = st.session_state.df  # Retrieve stored data
    st.write("Nothing here yet!")
else:
    st.warning("💡 Hint: No data available. Please visit the Data Fetcher page quickly and come back to this page.")