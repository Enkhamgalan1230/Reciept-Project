import streamlit as st

st.title("Helper", anchor=False)
st.markdown("---")

st.subheader("Frequently Asked Questions (FAQ)", anchor=False)
expander1 = st.expander
expander2 = st.expander
expander3 = st.expander
expander4 = st.expander
expander5 = st.expander
expander6 = st.expander
expander7 = st.expander
expander8 = st.expander
expander9 = st.expander
expander10 = st.expander
expander11 = st.expander
expander12 = st.expander

st.caption("Data Issues")
with expander2("Hint: No data available"):
    col1, col2, col3 = st.columns([1, 2, 1])  # middle column is 2x wider
    with col2:
        st.image("assets/hint.png", use_container_width=True)

    st.markdown(
        "• If no data appears to be available, please do not be concerned. "
        "All previously fetched data is securely stored in the application's cache, allowing for efficient reuse without requiring a fresh retrieval every time. "
        "To populate or refresh the dataset manually, you may simply navigate to the "
        "[Data Fetcher](./data_fetcher) page, where the application will retrieve the most recent information available from our database."
    )

with expander3("How often data gets updated."):
    st.markdown(
        "• If no data appears to be available, please do not be concerned. "
        "The data is refreshed on a **weekly** basis to maintain accuracy and relevance. "
        "Updates typically occur every 7 days, depending on the availability of new information from our sources. "
        "If cached data is being used, it will automatically update the next time the app detects a change following the update cycle. "
    )

with expander4("How data gets collected?"):
    st.markdown(
        "We collect data through publicly available sources which includes supermarket websites. " 
        "All data is gathered responsibly, with a focus on accuracy and relevance, and is used solely to enhance the app’s functionality and user experience."
        "\n\nYou may also visit the [Data Collection](./data_collection) page to view the process"
    )

with expander5("What kind of data does the app collect?"):
    st.markdown(
        "The app collects grocery prices, product details, store locations, and publicly available information from supermarkets. " \
        "If users choose to use certain features, the app may also collect location data, shopping preferences, or budget inputs to personalise the experience. " \
        "**No sensitive personal data** is collected without consent."
    )
st.caption("Price Comparison")
with expander7("What does the price comparison dashboard show?"):
    st.markdown(
        "The dashboard displays the **latest prices** for 15 commonly purchased grocery items across five major UK supermarkets. "
        "It highlights the **cheapest store** for each product and provides a visual comparison to assist with budgeting."
    )

with expander8("How does the product search work?"):
    st.markdown(
        "The product search feature allows you to enter keywords (e.g., 'chicken breast 400g') to find exact matches across your selected stores and subcategories. "
        "Only results containing **all keywords** in your query will be shown, sorted by the lowest price."
    )

with expander8("It doesn't show what I searched, why?"):
    st.markdown(
        "The product search feature allows you to enter keywords (e.g., 'chicken breast 400g') to find exact matches across your selected stores and subcategories. "
        "Please be precise on using keywords (e.g., Bad example: 'chicken', Good example: 'panko chicken breast') which will help the engine to find exact items."
    )


