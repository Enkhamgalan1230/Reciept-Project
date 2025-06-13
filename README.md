<h1 align="center">🧾 Receipt Project</h1> <p align="center"> <strong>Smart Budgeting and Grocery Price Comparison for Students</strong><br> <a href="https://receipt-entwan.streamlit.app/" target="_blank">🌐 Live App</a> • <a href="#features">📦 Features</a> • <a href="#tech-stack">🛠️ Tech Stack</a> • <a href="#project-status">🚧 Status</a> </p> <p align="center"> <img src="https://github.com/Enkhamgalan1230/Reciept-Project/blob/3133878d2ce323698609ca38f00fa978ca02fdff/assets/qr-code.png" alt="QR Code" width="160"/> </p>

# 📖 Introduction

The Receipt App is a smart budgeting and price prediction tool built to support UK university students facing the cost of living crisis. It helps users compare supermarket prices, track inflation trends, and generate grocery lists tailored to their budget and location.

Whether you're planning a weekly shop or looking for the cheapest essentials, Receipt gives you real-time, AI-assisted, and location-aware recommendations all in one platform.

💡 Offline-ready datasets are available in the /Supermarket data folder in case the live database is unavailable.

# ✨ Features

## 🛒 Price Comparison

Compare up to 15 grocery items across Tesco, Asda, Aldi, Waitrose, and Sainsbury’s.

Prices are fetched from real-time data (scraped or cached).

Supports advanced filters: subcategory, store, and keyword.

Visual bar charts show cheapest options clearly.

## 📈 Price Inflation Tracker

Displays week-to-week inflation across subcategories.

Supports store-specific price tracking.

Colour-coded percentage changes (🔺 increases / 🔻 decreases).

Handles missing data gracefully.

## 📍 Nearest Store Finder

Locate nearby supermarket branches via geolocation or postcode.

Uses OpenStreetMap Nominatim and Photon API for accurate mapping.

Results shown in a searchable table + interactive map.

## 🧾 Receipt Generator

Input groceries via:

Typing

Voice input

Conversational AI assistant

Uses NLP, fuzzy matching, and semantic search to match items.

Generates a shopping list optimised for:

Budget

Store selection

Essential vs optional items

Authenticated users can save their lists securely.

## 🔐 Authentication & Saved Lists

User sign-up/login via Supabase Auth.

Each saved list includes:

Items requested

Matched items and prices

Store selected

Timestamp

"My List" page shows past purchases and a 'Potential Buy' breakdown.
