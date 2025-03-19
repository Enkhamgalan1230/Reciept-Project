import streamlit as st
import requests
import pandas as pd
from geopy.distance import geodesic

# Function to fetch user's location
def get_user_location():
    response = requests.get("https://ipinfo.io/json")  # Backup IP-based geolocation
    location = response.json()
    lat, lon = map(float, location["loc"].split(","))
    return lat, lon

# Function to get nearby supermarkets
def get_nearby_stores(lat, lon, radius=5000, limit=5):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": "tesco",
        "format": "json",
        "lat": lat,
        "lon": lon,
        "radius": radius,
        "limit": limit
    }
    
    headers = {
        "User-Agent": "MyStreamlitApp/1.0 (zaecisama@gmail.com)"  # Replace with your email
    }

    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            st.error("Error decoding JSON. API might be rate-limited.")
            return []
    else:
        st.error(f"Failed to fetch nearby supermarkets. Status code: {response.status_code}")
        return []
# Function to find the closest store
def find_closest_store(user_lat, user_lon, stores):
    user_location = (user_lat, user_lon)
    closest_store = min(
        stores,
        key=lambda store: geodesic(user_location, (float(store["lat"]), float(store["lon"]))).km
    )
    distance = geodesic(user_location, (float(closest_store["lat"]), float(closest_store["lon"]))).km
    return closest_store["display_name"], float(closest_store["lat"]), float(closest_store["lon"]), distance

# Streamlit UI
st.title("Find Your Closest Supermarket 🛒")

if st.button("Get Location"):
    user_lat, user_lon = get_user_location()
    st.success(f"Your Location: **({user_lat}, {user_lon})**")

    # Get nearby supermarkets
    stores = get_nearby_stores(user_lat, user_lon)

    if stores:
        # Find closest store
        closest_store, store_lat, store_lon, distance = find_closest_store(user_lat, user_lon, stores)
        
        st.success(f"**Closest Store:** {closest_store}")
        st.write(f"📍 **Distance:** {distance:.2f} km")

        # Map visualization
        locations = pd.DataFrame(
            [[user_lat, user_lon]] + [[float(s["lat"]), float(s["lon"])] for s in stores],
            columns=["lat", "lon"]
        )
        st.map(locations)
    else:
        st.error("No supermarkets found nearby. Try again!")