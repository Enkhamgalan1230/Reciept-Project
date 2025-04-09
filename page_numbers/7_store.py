import streamlit as st
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation
from streamlit_folium import folium_static
import folium
import requests
import pandas as pd

st.header("Closest Store Finder 📍")
st.caption("💡 For security reasons you can erase your location from the session.")

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


container1 = st.container(border=True)
with container1:
    st.markdown("### 🌍 Choose how you'd like to use your location")
    st.caption("You can either use your real-time location or enter a UK postcode.")

    # ========== Location Mode Selection ==========
    location_mode = st.radio(
            "📌 Location Mode",
            ["📍 Use my current location", "🏡 Enter postcode manually"],
            key="location_mode",
            label_visibility="collapsed"  # Hide label to rely on markdown title above

        )
    user_lat = user_lon = None

    st.markdown("---")
    unit = st.radio("Choose distance unit:", ["km", "miles"], horizontal=True)
    #st.markdown("---")

    distance_input = st.number_input(
        f"📏 Enter maximum distance (in {unit}) to search for nearby stores:",
        min_value=1.0,
        max_value=50.0,
        value=5.0,
        step=0.5,
        placeholder='Distance'
    )

    # Convert miles to km if needed
    max_distance_km = distance_input * 1.609 if unit == "miles" else distance_input

    # ========== OPTION 1: Current Geolocation ==========
    if st.session_state["location_mode"] == "📍 Use my current location":
        if st.session_state.get("reset_checkbox"):
            st.session_state["check_location"] = False
            del st.session_state["reset_checkbox"]
            st.rerun()

        st.checkbox("✅ Check my location", key="check_location")

        if st.session_state.get("check_location"):
            loc = get_geolocation()
            if loc and "coords" in loc:
                user_lat = loc["coords"].get("latitude")
                user_lon = loc["coords"].get("longitude")
                if user_lat and user_lon:
                    st.toast("📍 Your location has been captured.", icon="✅")
                    st.session_state["user_lat"] = user_lat
                    st.session_state["user_lon"] = user_lon

                    if st.button("🧹 Forget my location", use_container_width=True):
                        st.session_state.pop("user_lat", None)
                        st.session_state.pop("user_lon", None)
                        st.session_state["reset_checkbox"] = True
                        st.toast("📍 Your location has been removed.", icon="🗑️")
                        st.rerun()

    # ========== OPTION 2: Manual Postcode ==========
    elif st.session_state["location_mode"] == "🏡 Enter postcode manually":
        postcode = st.text_input("Enter your UK postcode (e.g., W1A 1AA)")
        if postcode:
            geo_url = "https://nominatim.openstreetmap.org/search"
            geo_params = {
                "q": postcode,
                "format": "json",
                "addressdetails": 1,
                "countrycodes": "gb",
                "limit": 1
            }
            geo_res = requests.get(geo_url, params=geo_params, headers={"User-Agent": "ReceiptApp"})
            if geo_res.status_code == 200 and geo_res.json():
                location_data = geo_res.json()[0]
                user_lat = float(location_data["lat"])
                user_lon = float(location_data["lon"])
                st.success(f"✅ Location found for postcode: {postcode}")
            else:
                st.error("❌ Couldn't find coordinates for this postcode.")
    

    # ========== Store Search Logic ==========
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
            distance = geodesic((user_lat, user_lon), (store_lat, store_lon)).km

            if distance <= max_distance_km:
                found_stores.append({
                    "Store": store_name,
                    "Address": store_address,
                    "Distance": round(distance, 2),
                    "Latitude": store_lat,
                    "Longitude": store_lon
                })

        return found_stores

    # ========== Run Search if Location Available ==========
    if user_lat and user_lon:

        store_names = ["Tesco", "Sainsbury's", "Waitrose", "Asda", "Aldi"]
        all_stores = []

        for store in store_names:
            results = get_store_locations(store, user_lat, user_lon, max_distance_km)
            all_stores.extend(results)

        all_stores = sorted(all_stores, key=lambda x: x["Distance (km)"])

        if all_stores:
            df = pd.DataFrame(all_stores)
            st.success(f"🎯 Found {len(df)} store(s) within {max_distance_km}{unit}!")
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
                    popup=f"{row['Store']} ({row['Distance']}{unit})",
                    tooltip=row["Store"],
                    icon=folium.Icon(color="green", icon="shopping-cart")
                ).add_to(m)

            folium_static(m)
        else:
            st.warning("⚠️ No stores found within the specified range.")