import folium
import pandas as pd
import requests
import streamlit as st
from geopy.distance import geodesic
from streamlit_folium import folium_static
from streamlit_js_eval import get_geolocation


st.header("Closest Store Finder", anchor=False)
st.write("Find nearby supermarkets using your current location or a UK postcode.")


def find_supermarkets(latitude, longitude, radius_km):
    """Query mapped supermarket objects within a radius using OpenStreetMap."""
    radius_m = int(radius_km * 1000)
    query = f"""
    [out:json][timeout:25];
    (
      node[shop=supermarket](around:{radius_m},{latitude},{longitude});
      way[shop=supermarket](around:{radius_m},{latitude},{longitude});
      relation[shop=supermarket](around:{radius_m},{latitude},{longitude});
    );
    out center tags;
    """
    try:
        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
            headers={"User-Agent": "ReceiptApp/1.0"},
            timeout=35,
        )
        response.raise_for_status()
        elements = response.json().get("elements", [])
    except (requests.RequestException, ValueError) as error:
        st.error(f"The map service is temporarily unavailable: {error}")
        return []

    known_brands = ("tesco", "sainsbury", "waitrose", "asda", "aldi", "morrisons", "lidl", "iceland", "co-op", "coop")
    stores = []
    seen = set()
    for element in elements:
        tags = element.get("tags", {})
        name = tags.get("name") or tags.get("brand")
        if not name or not any(brand in name.casefold() for brand in known_brands):
            continue
        center = element.get("center", {})
        store_lat = element.get("lat", center.get("lat"))
        store_lon = element.get("lon", center.get("lon"))
        if store_lat is None or store_lon is None:
            continue
        distance = geodesic((latitude, longitude), (store_lat, store_lon)).km
        key = (name.casefold(), round(store_lat, 5), round(store_lon, 5))
        if key in seen:
            continue
        seen.add(key)
        stores.append({
            "Store": name,
            "Distance": round(distance, 2),
            "Latitude": store_lat,
            "Longitude": store_lon,
        })
    return sorted(stores, key=lambda store: store["Distance"])


with st.container(border=True):
    location_mode = st.radio(
        "Location method",
        ["Use my current location", "Enter postcode manually"],
        key="location_mode",
        horizontal=True,
    )
    user_lat = st.session_state.get("user_lat")
    user_lon = st.session_state.get("user_lon")

    if location_mode == "Use my current location":
        if st.checkbox("Share my current location", key="check_location"):
            location = get_geolocation()
            if location and location.get("coords"):
                user_lat = location["coords"].get("latitude")
                user_lon = location["coords"].get("longitude")
                if user_lat is not None and user_lon is not None:
                    st.session_state.user_lat = float(user_lat)
                    st.session_state.user_lon = float(user_lon)
                    st.success("Location captured.")
        if user_lat is not None and st.button("Forget saved location"):
            st.session_state.pop("user_lat", None)
            st.session_state.pop("user_lon", None)
            st.session_state.check_location = False
            st.rerun()
    else:
        postcode = st.text_input("UK postcode", placeholder="e.g. W1A 1AA")
        if postcode:
            try:
                response = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": postcode, "format": "json", "countrycodes": "gb", "limit": 1},
                    headers={"User-Agent": "ReceiptApp/1.0"},
                    timeout=10,
                )
                response.raise_for_status()
                matches = response.json()
            except (requests.RequestException, ValueError) as error:
                st.error(f"Could not find that postcode: {error}")
                matches = []
            if matches:
                user_lat = float(matches[0]["lat"])
                user_lon = float(matches[0]["lon"])
                st.session_state.user_lat = user_lat
                st.session_state.user_lon = user_lon
                st.success(f"Location found for {postcode.upper()}.")

    unit = st.radio("Distance unit", ["km", "miles"], horizontal=True)
    distance = st.number_input("Search radius", min_value=1.0, max_value=50.0, value=5.0, step=0.5)

if user_lat is not None and user_lon is not None:
    stores = find_supermarkets(user_lat, user_lon, distance * 1.609 if unit == "miles" else distance)
    if stores:
        results = pd.DataFrame(stores)
        if unit == "miles":
            results["Distance"] = (results["Distance"] / 1.609).round(2)
        distance_column = f"Distance ({unit})"
        results.rename(columns={"Distance": distance_column}, inplace=True)
        st.success(f"Found {len(results)} supermarket(s) within {distance:g} {unit}.")
        st.dataframe(results[["Store", distance_column]], use_container_width=True, hide_index=True)

        st.subheader("Store Locations Map", anchor=False)
        map_view = folium.Map(location=[user_lat, user_lon], zoom_start=14)
        folium.Marker([user_lat, user_lon], popup="Your location", icon=folium.Icon(color="blue", icon="user")).add_to(map_view)
        logo_paths = {
            "tesco": "assets/tesco.png",
            "asda": "assets/asda.png",
            "aldi": "assets/aldi.png",
            "sainsbury": "assets/sainsbury.png",
            "waitrose": "assets/waitrose.png",
        }
        for store in stores:
            logo = next((path for brand, path in logo_paths.items() if brand in store["Store"].casefold()), None)
            marker_icon = folium.CustomIcon(logo, icon_size=(42, 42)) if logo else folium.Icon(color="green", icon="shopping-cart")
            maps_link = f"https://www.google.com/maps/search/?api=1&query={store['Latitude']},{store['Longitude']}"
            popup = f"<b>{store['Store']}</b><br>Distance: {store['Distance']} km<br><a href='{maps_link}' target='_blank'>Open in Google Maps</a>"
            folium.Marker([store["Latitude"], store["Longitude"]], popup=folium.Popup(popup, max_width=320), tooltip=store["Store"], icon=marker_icon).add_to(map_view)
        folium_static(map_view)
    else:
        st.info("No mapped supermarkets were found in that radius. Try increasing the search radius.")
else:
    st.info("Choose a location method above to search for nearby supermarkets.")
