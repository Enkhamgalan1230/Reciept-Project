import streamlit as st
import requests
import pandas as pd
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation
from streamlit_folium import folium_static
import folium

# 🎨 Add Styling
st.title("🛒 Receipt 📃")
st.markdown("---")
st.subheader("🔍 Closest Store Finder 📍")

# ℹ️ Info message
st.info("👇 Please tick the checkbox to capture your location.")

# 🌍 Function to get store locations
def get_store_locations(store_name, user_lat, user_lon, max_distance_km):
    url = "https://photon.komoot.io/api/"
    params = {
        "q": store_name,  
        "lat": user_lat,
        "lon": user_lon,
        "limit": 10
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        return []

    try:
        data = response.json()
        places = data.get("features", [])
    except requests.exceptions.JSONDecodeError:
        return []

    found_stores = []
    for place in places:
        coords = place["geometry"]["coordinates"]
        store_lon, store_lat = coords[0], coords[1]
        store_address = place["properties"].get("name", "Unknown store")

        # Calculate distance
        distance = geodesic((user_lat, user_lon), (store_lat, store_lon)).km

        if distance <= max_distance_km:
            found_stores.append({
                "Store": store_name,
                "Address": store_address,
                "Distance (km)": round(distance, 2),
                "Latitude": store_lat,
                "Longitude": store_lon
            })

    return found_stores

# 📍 Check user location
if st.checkbox("✅ Check my location"):
    loc = get_geolocation()
    if loc and "coords" in loc:
        user_lat = loc["coords"].get("latitude")
        user_lon = loc["coords"].get("longitude")

        if user_lat and user_lon is not None: 
            st.success("📍 Location Captured!")

        # Define search parameters
        max_distance_km = 5
        store_names = ["Tesco", "Sainsbury's", "Waitrose", "Asda", "Aldi"]

        all_stores = []
        for store in store_names:
            stores = get_store_locations(store, user_lat, user_lon, max_distance_km)
            all_stores.extend(stores)

        # 🔽 Sort stores by distance (nearest first)
        all_stores = sorted(all_stores, key=lambda x: x["Distance (km)"])

        # 📊 Display Results
        if all_stores:
            df = pd.DataFrame(all_stores)
            st.success(f"🎯 Found {len(df)} stores within {max_distance_km} km!")
            st.dataframe(df)

            # 🗺️ Create Map
            st.subheader("🗺️ Store Locations Map")

            # 🌍 Initialize Map
            m = folium.Map(location=[user_lat, user_lon], zoom_start=13)

            # 🔵 Add User Location Marker
            folium.Marker(
                [user_lat, user_lon], 
                popup="📍 You are here",
                icon=folium.Icon(color="blue", icon="user")
            ).add_to(m)

            # 🛒 Add Store Markers
            for _, row in df.iterrows():
                folium.Marker(
                    [row["Latitude"], row["Longitude"]],
                    popup=f"{row['Store']} ({row['Distance (km)']} km)",
                    tooltip=row["Store"],
                    icon=folium.Icon(color="green", icon="shopping-cart")
                ).add_to(m)

            # 🌍 Show Map
            folium_static(m)

        else:
            st.warning("⚠️ No stores found within the specified range.")