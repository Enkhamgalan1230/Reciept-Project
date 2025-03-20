import streamlit as st
import requests
import pandas as pd
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation

if st.button("Check my Location"):
    loc = get_geolocation()
    st.write(f"Your coordinates are {loc}")
   