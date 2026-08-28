"""Load the product snapshots shipped with the project."""

from pathlib import Path
import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).resolve().parent / "Supermarket data" / "Clean"


@st.cache_data(show_spinner=False)
def load_product_data():
    files = sorted(DATA_DIR.glob("*/*.csv"))
    if not files:
        raise FileNotFoundError(f"No cleaned product CSV files found in {DATA_DIR}")
    frames = [pd.read_csv(path, low_memory=False) for path in files]
    data = pd.concat(frames, ignore_index=True)
    for column in ("Price", "Year", "Month", "Day", "Unit_each", "Unit_kg", "Unit_litre"):
        if column in data:
            data[column] = pd.to_numeric(data[column], errors="coerce")
    return data
