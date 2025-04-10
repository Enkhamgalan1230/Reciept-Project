import streamlit as st

st.title("Helper", anchor=False)
st.markdown("---")

st.subheader("FAQ", anchor=False)

with st.expander("💡 Hint: No data available"):
    st.image("assets/hint.png", caption="Cached data hint", use_column_width=True)
    st.markdown(
        "Do not worry, we store the data in cache so you can simply visit the "
        "[Data Fetcher](./data_fetcher) page."
    )