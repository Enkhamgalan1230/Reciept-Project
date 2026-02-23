<h1 align="center">🧾 Receipt Project</h1> 
<p align="center">
  <strong>Smart Budgeting and Grocery Price Comparison for Students</strong><br>
  <a href="https://receipt-entwan.streamlit.app/" target="_blank">🌐 Live App</a> • 
  <a href="#-features">📦 Features</a> • 
  <a href="#-tech-stack">🛠️ Tech Stack</a> • 
  <a href="#-project-status">🚧 Status</a>
</p>

<p align="center">
  <img src="https://github.com/Enkhamgalan1230/Reciept-Project/blob/3133878d2ce323698609ca38f00fa978ca02fdff/assets/qr-code.png" alt="QR Code" width="160"/>
</p>

# 🚨 Update 

Currently, the platform and project are offline because the database host requires frequent requests to remain active. However, you can contact me to get the data and tutorial for setting up the database/scrapers.

# 📖 Introduction

The Receipt App is a smart budgeting and price prediction tool built to support UK university students facing the cost of living crisis. It helps users compare supermarket prices, track inflation trends, and generate grocery lists tailored to their budget and location.

Whether you're planning a weekly shop or looking for the cheapest essentials, Receipt gives you real-time, AI-assisted, and location-aware recommendations all in one platform.

💡 Offline-ready datasets are available in the /Supermarket data folder in case the live database is unavailable.

# ✨ Features

## 🛒 Price Comparison

1. Compare up to 15 grocery items across Tesco, Asda, Aldi, Waitrose, and Sainsbury’s.
2. Prices are fetched from real-time data (scraped or cached).
3. Supports advanced filters: subcategory, store, and keyword.
4. Visual bar charts show cheapest options clearly.

## 📈 Price Inflation Tracker

1. Displays week-to-week inflation across subcategories.
2. Supports store-specific price tracking.
3. Colour-coded percentage changes (🔺 increases / 🔻 decreases).
4. Handles missing data gracefully.

## 📍 Nearest Store Finder

1. Locate nearby supermarket branches via geolocation or postcode.
2. Uses OpenStreetMap Nominatim and Photon API for accurate mapping.
3. Results shown in a searchable table + interactive map (Google Maps API).

## 🧾 Receipt Generator

1. Input groceries via:
   - Typing
   - Voice input
   - Conversational AI assistant (LLaMa)

2. Uses NLP, fuzzy matching, and semantic search to match items.
3. Generates a shopping list optimised for:
   - Budget
   - Store selection
   - Essential vs optional items
   - Authenticated users can save their lists securely.

## 🔐 Authentication & Saved Lists

1. User sign-up/login via Supabase Auth.
2. Each saved list includes:
   - Items requested
   - Matched items and prices
   - Store selected
   - Timestamp

"My List" page shows past purchases and a 'Potential Buy' breakdown.

# 🎯 Target Audience

Originally built for university students in the UK, the app is also valuable for anyone looking to:

- Cut down on food expenses
- Forecast short-term price changes
- Shop smarter during inflation

# 🛠️ Tech Stack

| Technology                | Purpose                                       |
| ------------------------- | --------------------------------------------- |
| **Streamlit**             | Frontend + app UI                             |
| **Supabase**              | Backend database + user authentication        |
| **Python**                | Core logic, data scraping, and utilities      |
| **sentence-transformers** | Semantic product matching (embeddings)        |
| **NLP + fuzzywuzzy**      | Phrase extraction & fuzzy matching            |
| **LLaMA via Groq API**    | Conversational AI assistant for receipt input |
| **Photon/Nominatim API**  | Store geolocation and address lookup          |

# 🚧 Project Status

| Module                          | Status |
|---------------------------------|--------|
| Data Scraping                   | ✅     |
| Preprocessing & Generalisation  | ✅     |
| Supabase Integration            | ✅     |
| Cloud Deployment                | ✅     |
| Price Comparison Logic          | ✅     |
| Store Locator                   | ✅     |
| User Authentication             | ✅     |
| Receipt Generator               | ✅     |
| Price Prediction                | ✅     |
| Joy in Life                     | ✅     |

# 🧠 Future Enhancements

1. Long-term price forecasting (LSTM/XGBoost models)
2. iOS/Android mobile app version
3. Social sharing of lists & budget tips
4. More international stores support

# 📬 Feedback & Contribution

Contact me on [LinkedIn](https://www.linkedin.com/in/entwan/) if you have any questions or would like to collaborate.

