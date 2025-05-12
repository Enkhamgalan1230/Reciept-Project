# Reciept-Project

👉 https://receipt-entwan.streamlit.app/ 👈

### Project Overview: Smart Budgeting and Price Prediction App for University Students

**Introduction**

In light of the ongoing cost of living crisis, many university students in the UK are facing
increasing financial pressures. The need for effective budgeting tools has never been more
critical. To address this issue, I propose developing a Smart Budgeting and Price Prediction
App tailored specifically for university students. This app will assist users in managing their
expenses, comparing grocery prices, and anticipating future price changes, empowering them
to make informed purchasing decisions. 

### Key Features and Functionality

**1. Price Comparison**

* The app retrieves the most recent grocery prices from major UK supermarkets, using either integrated APIs or regularly updated scraped data stored in session state.
* Users can compare the prices of up to 15 popular items side by side across Tesco, Asda, Aldi, Waitrose, and Sainsbury’s, with a clear display of the cheapest option for each product.
* Products are visualised in a bar chart format, enabling users to quickly identify price differences and make cost-effective choices.
* Even when a product is not available in certain stores, the system accounts for this by indicating missing data while maintaining consistent layout and comparison structure.
* An advanced search functionality allows users to filter items by subcategory, store, or specific keywords. The comparison table displays the filtered results sorted by price, along with units and discount prices, enabling precise and informed decision-making.

**2. Price Inflation Status**

* The app enables users to monitor short-term price fluctuations by comparing the average cost of subcategories across two consecutive data collection dates (typically weekly).
* Users can select a specific supermarket to view how average prices have changed over time for each product subcategory.
* The interface presents a dynamic inflation board, where each subcategory is displayed as a separate metric showing the latest average price and the percentage change from the previous week.
* The inflation percentage is colour-coded to reflect increases or decreases in price, helping users quickly identify inflationary trends and assess store performance.
* In the event of missing data for a given subcategory, the system ensures continuity by filling values appropriately and defaulting to a 0% change where necessary, maintaining the consistency and reliability of insights.

**3. Nearest Store Finder**

* This feature enables users to locate the closest branches of major UK supermarkets based on either their current geolocation or a manually entered UK postcode.
* Users can customise the search radius and select between distance units (kilometres or miles) to suit their preferences, enhancing flexibility.
* When opting to use their current location, users can grant access to geolocation services, and the system will retrieve their coordinates securely. Alternatively, they may input a UK postcode, which is converted to latitude and longitude using the OpenStreetMap Nominatim API.
* Once the user’s location is obtained, the app queries the Photon API to identify nearby stores (Tesco, Sainsbury’s, Waitrose, Asda, Aldi) within the specified range.
* The results are presented in a structured table displaying store names, addresses, and exact distances from the user, allowing for informed decisions regarding accessibility and convenience.
* A dynamic map visualises the user’s location alongside nearby store locations, using interactive markers to provide an intuitive spatial understanding of store proximity.

**4. Receipt**

* This feature enables users to generate a budget-conscious shopping list using a combination of input methods typed, spoken, or assisted by an AI-powered conversational assistant.
* Users may manually type essential or optional grocery items, speak their list using integrated voice recognition, or describe their preferences and meal plans to the AI assistant, which then suggests specific products based on user intent.
* Natural language processing (NLP), fuzzy string matching, and semantic search are applied to extract and match input phrases to real product names in the database while filtering out unsuitable items such as snacks, beverages, processed goods, or dietary substitutes—unless explicitly permitted.
* Once all items are gathered, the system matches them against the latest prices from a selected store (e.g., Tesco, Asda, Aldi) and filters the list based on a user-defined budget.
* The algorithm prioritises essential items first and fills remaining budget with optional extras where possible. Items that cannot fit within the budget are clearly indicated.
* The final list includes matched items, their prices, discounts, and the originating store. A summary of total cost is displayed to support informed decision-making.
* Users who are signed in can save their generated shopping lists to a secure Supabase database, where items, matched products, selected store, and timestamps are recorded for future access and reference.

**5. User Authentication and Personalised List Management**

* The application includes a secure login system that allows users to create personal accounts and access tailored features, such as saving and reviewing past shopping lists.
* Authentication is managed through Supabase Auth, ensuring that user credentials are handled securely and access to data is appropriately restricted based on identity.
* Once authenticated, users can save their generated shopping lists directly to the Supabase database. Each saved list is associated with the user’s email, the selected store, the original input items, the matched product details, and the timestamp of creation.
* A dedicated "My List" page enables users to review previously saved shopping lists. These entries are presented in a structured format, including a breakdown of matched items and associated stores, allowing users to reflect on past spending decisions.
* For each entry, the application clearly distinguishes between the user’s original requests and the final selected products. A supplementary section labelled "Potential Buy" provides a concise summary of the items matched under the defined budget.

### Target Audience

The primary target audience for this app is university students in the UK who are seeking
eƯective tools to manage their finances in a challenging economic environment or basically anyone. The app aims
to empower whoever by providing them with valuable financial insights and cost-saving
strategies. 


**Current progress:**

* Data gathering scraper: ✔️
* Pre-processing, cleaning, generalising: ✔️
* Database setup:✔️
* Cloud application:✔️
* Comparison logic:✔️
* Store Logic: ✔️
* User Authentication: ✔️
* Receipt Generator Logic: ✔️
* Joy in Life: ✔️
* Price prediction: ✔️


Next Step: DOne innit

