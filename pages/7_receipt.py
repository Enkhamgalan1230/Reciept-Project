import streamlit as st
import requests
import pandas as pd
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation
from streamlit_folium import folium_static
import folium


st.title("🛒 Receipt 📃", anchor=False)
st.markdown("---")
st.subheader("🔍 Closest Store Finder 📍", anchor=False)

# ℹ Info message
st.info("👇 Please tick the checkbox to capture your location.")

comment = '''
This function searches for a given store name near the user's location using the Photon API, 
retrieves up to 10 possible store locations, filters them based on whether they are within the specified distance (max_distance_km), 
and returns a list of stores with their names, addresses, coordinates, and distances from the user. 

It first sends a request to the API with the store name and user's latitude and longitude, then processes the response, 
extracts relevant store details, calculates the geographical distance using the geodesic function, and only keeps stores that fall within the given range. 
If the API request fails or returns invalid data, the function safely handles errors and returns an empty list.

geopy.distance - gets distance between two lon and lat.

The Photon API-  is an OpenStreetMap-based geolocation API that allows us to search for places using natural language queries. 
It provides latitude, longitude, address details, and other metadata for a given search term

We send a GET request to https://photon.komoot.io/api/ with search parameters.
The API matches the query (for example, "Tesco near 51.6275938,-0.7519156") to its OpenStreetMap database.
It returns a JSON response containing a list of locations (if foond.)
'''

# Function to get store locations
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
        data = response.json()  # Convert response JSON into a Python dictionary
        places = data.get("features", [])  # Extract the list of store locations (default to an empty list if not found)
    except requests.exceptions.JSONDecodeError:
        return []

    found_stores = []
    #Loop through each store result returned by the API
    for place in places:
        coords = place["geometry"]["coordinates"] # Extract coordinates
        store_lon, store_lat = coords[0], coords[1]  # Assign longitude and latitude
        store_address = place["properties"].get("name", "Unknown store") # Extract store names; if missing turn to "Unknown store"


        distance = geodesic((user_lat, user_lon), (store_lat, store_lon)).km # Calculate distance

        # If store is within the max allowed distance, add to results
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

    #Custom location finder found on community forum and returns a dictionary after user approval
    loc = get_geolocation()
    if loc and "coords" in loc:
        user_lat = loc["coords"].get("latitude")
        user_lon = loc["coords"].get("longitude")

        if user_lat and user_lon is not None: 
            st.success("📍 Location Captured!")

        # Define search parameters
        max_distance_km = 5
        store_names = ["Tesco", "Sainsbury's", "Waitrose", "Asda", "Aldi"]

        #Appending the found store info
        all_stores = []
        for store in store_names:
            stores = get_store_locations(store, user_lat, user_lon, max_distance_km)
            all_stores.extend(stores)

        # Sort stores by distance (nearest first)
        all_stores = sorted(all_stores, key=lambda x: x["Distance (km)"])

        # Display Results
        if all_stores:
            df = pd.DataFrame(all_stores)
            st.success(f"🎯 Found {len(df)} stores within {max_distance_km} km!")
            st.dataframe(df)

            st.subheader("🗺️ Store Locations Map", anchor=False)

            # Initialising the Map
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

st.subheader("Shopping List generator 📃")

container = st.container(border= True)

container.write("How much is the budget and the duration?")

day = ["A Day", "A Week", " Two Week", "Month"]
duration = container.pills(label = "Duration",options = day, selection_mode="single")
budget = container.number_input("Insert the value (£)", placeholder= "Ex : 30", format="%0.2f", min_value = 0.0)

