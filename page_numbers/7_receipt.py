import streamlit as st
import requests
import pandas as pd
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation
from streamlit_folium import folium_static
import folium
from streamlit_tags import st_tags
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import tempfile
import spacy
from fuzzywuzzy import process
import subprocess
import importlib

st.title("🛒 Receipt 📃", anchor=False)
st.markdown("---")
container1 = st.container(border= True)
with container1:
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

container2 = st.container(border= True)

with container2:
    st.write("How much is the budget and the duration?")

    day = ["a Day", "a Week", " Two Week", "a Month"]
    duration = st.pills(label = "Duration",options = day, selection_mode="single")
    # Set default duration text

    budget = st.number_input(f"Insert the budget (£)", placeholder= "Ex : 30", format="%0.2f", min_value = 0.0)

    essential_list = st_tags(
        label='Enter your essential products:',
        text='Press enter to add more',
        value=[],
        suggestions=["Milk","Bread","Eggs","Potatoes","Bananas","Bacon","Butter","Juice","Biscuits"
                    "Strawberries", "Cola", "Canned Tuna", "Blueberries", "Granola", ],
        maxtags=40,
        key='essential_input'
    )

    secondary_list = st_tags(
        label='Would love to buy these if we can:',
        text='Press enter to add more',
        value=[],
        suggestions=["Milk","Bread","Eggs","Potatoes","Bananas","Bacon","Butter","Juice","Biscuits"
                    "Strawberries", "Cola", "Canned Tuna", "Blueberries", "Granola", ],
        maxtags=40,
        key='extra_input'
    )

    st.write("Products List:",essential_list, secondary_list)

    st.markdown("🎧 **Click to record your grocery list**")

    st.markdown("""
        <style>
        .stAudioRecorder button {
            background-color: #4CAF50;
            color: white;
            padding: 0.5em 1em;
            font-size: 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }
        .stAudioRecorder svg {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    audio = audio_recorder("Click here to record your voice", "Recording...")

    voice_products = []

    if audio is not None and len(audio) > 0:
        st.audio(audio, format="audio/wav")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio)
            temp_wav_path = f.name

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_wav_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                st.success(f"🗣️ You said: {text}")
                voice_products = [item.strip() for item in text.split(",")]
                st.write("📝 Products from voice:", voice_products)
            except sr.UnknownValueError:
                st.error("❌ Could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"❌ Could not request results; {e}")

    # Combine all product sources
    all_products = list(set(essential_list + secondary_list + voice_products))
    st.write("🧾 Final Products List:", all_products)

