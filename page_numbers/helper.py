import streamlit as st

st.title("Helper", anchor=False)
st.markdown("---")

st.subheader("Frequently Asked Questions FAQ", anchor=False)

with st.expander("Hint: No data available"):
    col1, col2, col3 = st.columns([1, 2, 1])  # middle column is 2x wider
    with col2:
        st.image("assets/hint.png", use_container_width=True)

    st.markdown(
        "• If no data appears to be available, please do not be concerned. "
        "All previously fetched data is securely stored in the application's cache, allowing for efficient reuse without requiring a fresh retrieval every time. "
        "To populate or refresh the dataset manually, you may simply navigate to the "
        "[Data Fetcher](./data_fetcher) page, where the application will retrieve the most recent information available from our sources."
    )

with st.expander("How often data gets updated."):
    st.markdown(
        "• If no data appears to be available, please do not be concerned. "
        "The data is refreshed on a **weekly** basis to maintain accuracy and relevance. "
        "Updates typically occur every 7 days, depending on the availability of new information from our sources. "
        "If cached data is being used, it will automatically update the next time the app detects a change following the update cycle. "
        "\n\nYou may also revisit the **Data Fetcher** page to view the most recent data manually."
    )

with st.expander("What does the price comparison dashboard show?"):
    st.markdown(
        "The dashboard displays the **latest prices** for 15 commonly purchased grocery items across five major UK supermarkets. "
        "It highlights the **cheapest store** for each product and provides a visual comparison to assist with budgeting."
    )

with st.expander("How does the product search work?"):
    st.markdown(
        "The product search feature allows you to enter keywords (e.g., 'chicken breast 400g') to find exact matches across your selected stores and subcategories. "
        "Only results containing **all keywords** in your query will be shown, sorted by the lowest price."
    )

