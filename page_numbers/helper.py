import streamlit as st

st.title("Helper", anchor=False)
st.markdown("---")

st.subheader("FAQ", anchor=False)

with st.expander("💡 Hint: No data available"):
    col1, col2, col3 = st.columns([1, 2, 1])  # middle column is 2x wider
    with col2:
        st.image("assets/hint.png", use_column_width=True)

    st.markdown(
        "Do not worry, we store the data in cache so you can simply visit the "
        "[Data Fetcher](./data_fetcher) page."
    )