import streamlit as st

# Check if df is stored in session state
if "df" in st.session_state:
    df = st.session_state.df  # Retrieve cached data
    st.write("📈 Product Statistics:")
    st.write(df.describe())  # Show statistics
else:
    st.write("⚠️ No data available. Please visit the Data Analysis page first.")