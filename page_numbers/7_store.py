import streamlit as st
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation
from streamlit_folium import folium_static
import folium
import requests
import pandas as pd

st.header("Closest Store Finder 📍")
st.caption("💡 You can either write or record your list")

container1 = st.container(border= True)
with container1:
    # ℹ Info message
    st.success("👇 Please tick the checkbox to capture your location.")

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

    # -- STEP 1: Handle forget location trigger first (BEFORE rendering checkbox)
    if st.session_state.get("reset_checkbox"):
        st.session_state["check_location"] = False  # Reset the checkbox
        del st.session_state["reset_checkbox"]      # Remove the flag
        st.rerun()  # Force rerun with updated state

    # -- STEP 2: Now render checkbox with key
    st.checkbox("✅ Check my location", key="check_location")

    # Check if checkbox is ticked
    if st.session_state.get("check_location"):
        loc = get_geolocation()

        if loc and "coords" in loc:
            user_lat = loc["coords"].get("latitude")
            user_lon = loc["coords"].get("longitude")

            if user_lat and user_lon is not None: 
                st.success("📍 Location Captured!")

                st.session_state["user_lat"] = user_lat
                st.session_state["user_lon"] = user_lon

                # Forget location button
                if st.button("🧹 Forget my location", use_container_width=True):
                    st.session_state.pop("user_lat", None)
                    st.session_state.pop("user_lon", None)

                    # ✅ Set flag for next rerun to reset checkbox
                    st.session_state["reset_checkbox"] = True
                    st.toast("📍 Your location has been removed from this session.", icon="🗑️")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            # --- Store Finder Logic ---
            max_distance_km = 5
            store_names = ["Tesco", "Sainsbury's", "Waitrose", "Asda", "Aldi"]
            all_stores = []

            for store in store_names:
                stores = get_store_locations(store, user_lat, user_lon, max_distance_km)
                all_stores.extend(stores)

            all_stores = sorted(all_stores, key=lambda x: x["Distance (km)"])

            if all_stores:
                df = pd.DataFrame(all_stores)
                st.success(f"🎯 Found {len(df)} stores within {max_distance_km} km!")
                st.dataframe(df)

                st.subheader("🗺️ Store Locations Map", anchor=False)
                m = folium.Map(location=[user_lat, user_lon], zoom_start=13)

                folium.Marker(
                    [user_lat, user_lon], 
                    popup="📍 You are here",
                    icon=folium.Icon(color="blue", icon="user")
                ).add_to(m)

                for _, row in df.iterrows():
                    folium.Marker(
                        [row["Latitude"], row["Longitude"]],
                        popup=f"{row['Store']} ({row['Distance (km)']} km)",
                        tooltip=row["Store"],
                        icon=folium.Icon(color="green", icon="shopping-cart")
                    ).add_to(m)

                folium_static(m)

            else:
                st.warning("⚠️ No stores found within the specified range.")
