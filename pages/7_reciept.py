import streamlit as st
import requests
import pandas as pd
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation

st.title("Reciept 📃")

st.markdown("---")

st.subheader("Closest store finder 📍")


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

# User's location (get from geolocation function)
if st.checkbox("Check my location"):
    loc = get_geolocation()
    if loc and "coords" in loc:
        user_lat = loc["coords"].get("latitude")
        user_lon = loc["coords"].get("longitude")

        if user_lat and user_lon is not None: 
            st.write(f"Location Captured ✅")

        # Define search parameters
        max_distance_km = 5
        store_names = ["Tesco", "Sainsbury's", "Waitrose", "Asda", "Aldi"]

        all_stores = []
        for store in store_names:
            stores = get_store_locations(store, user_lat, user_lon, max_distance_km)
            all_stores.extend(stores)

        # Display results
        if all_stores:
            df = pd.DataFrame(all_stores)
            st.write("Closest stores within 5 km:")
            st.dataframe(df)
        else:
            st.write("No stores found within the specified range.")