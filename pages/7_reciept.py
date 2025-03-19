from streamlit_geolocation import streamlit_geolocation
import streamlit as st


location = streamlit_geolocation()

st.write(location)