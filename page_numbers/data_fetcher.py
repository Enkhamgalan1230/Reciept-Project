import streamlit as st

from local_data import load_product_data


st.title("Data Fetcher Tool", anchor=False)
st.info("Product data is loaded from the cleaned CSV snapshots bundled with this project. No database connection is required.")

if "df" not in st.session_state:
    with st.spinner("Loading product data from disk..."):
        st.session_state.df = load_product_data()
    st.success(f"Loaded {len(st.session_state.df):,} product rows from local CSV files.")
else:
    st.write("Product data is already loaded for this session.")

st.dataframe(st.session_state.df.head(10), use_container_width=True)
