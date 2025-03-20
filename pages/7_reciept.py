import streamlit as st
import requests
import pandas as pd
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation

def get_store_locations(store_name, user_lat, user_lon, max_distance_km):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{store_name} near {user_lat},{user_lon}",  # Search for store near user
        "format": "json",
        "addressdetails": 1,
        "limit": 10,
        "extratags": 1
    }
    
    headers = {
        "User-Agent": "MyStreamlitApp/1.0 (contact: your-email@example.com)"  # Required!
    }

    response = requests.get(url, params=params, headers=headers)

    # Debugging: Print API response details
    print("\n--- DEBUG INFO ---")
    print("URL:", response.url)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text[:500])  # First 500 characters
    print("------------------\n")

    if response.status_code != 200:
        return []  # Return empty list if the API call fails

    try:
        data = response.json()
        if not data:
            print("Error: No data returned from API")
            return []
    except requests.exceptions.JSONDecodeError:
        print("Error: Unable to decode JSON response")
        return []

    found_stores = []
    for place in data:
        store_lat = float(place["lat"])
        store_lon = float(place["lon"])
        store_address = place.get("display_name", "Unknown address")

        # Calculate distance
        from geopy.distance import geodesic
        distance = geodesic((user_lat, user_lon), (store_lat, store_lon)).km

        # If within range, add to list
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
        st.write(f"Your coordinates are: Latitude {user_lat}, Longitude {user_lon}")

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