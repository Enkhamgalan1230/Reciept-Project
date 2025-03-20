import streamlit as st
import requests
import pandas as pd
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation

if st.checkbox("Check my location"):
    loc = get_geolocation()
    if loc and "coords" in loc:
        latitude = loc["coords"].get("latitude")
        longitude = loc["coords"].get("longitude")
        st.write(f"Your coordinates are: Latitude {latitude}, Longitude {longitude}")
    else:
        st.write("Could not retrieve location data.")


    
   