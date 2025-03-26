import streamlit as st
import requests
import pandas as pd
from streamlit_tags import st_tags
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import tempfile
import spacy
from fuzzywuzzy import process
import subprocess
import importlib

# Check if df is stored in session state
if "df" in st.session_state:
    df = st.session_state.df
else:
    st.warning("💡 Hint: No data available. Please visit the Data Fetcher page quickly and come back to this page.")

# Load spaCy English model once
nlp = spacy.load("en_core_web_sm")

# Load food adjectives from CSV
df_adj = pd.read_csv("food_adjectives.csv")
hyphenated_adjs = set(df_adj["Food_Adjective"].str.lower().tolist())

# Map phrases without hyphens to their hyphenated form
phrase_map = {adj.replace("-", " "): adj for adj in hyphenated_adjs}

def fix_multiword_adjectives(text):
    """Replace non-hyphenated multi-word phrases with correct hyphenated forms."""
    for plain, hyphenated in phrase_map.items():
        if plain in text:
            text = text.replace(plain, hyphenated)
    return text

def extract_adj_noun_phrases(text):
    doc = nlp(text)
    phrases = []
    used_indices = set()

    # Phase 1: Handle 4-token hyphenated adjectives: full - fat + milk
    i = 0
    while i < len(doc) - 3:
        t1, t2, t3, t4 = doc[i], doc[i + 1], doc[i + 2], doc[i + 3]

        if t1.pos_ == "ADJ" and t2.text == "-" and t4.pos_ == "NOUN":
            hyphenated = f"{t1.text.lower()}-{t3.text.lower()}"
            phrases.append(f"{hyphenated} {t4.text.lower()}")
            used_indices.update({i, i + 1, i + 2, i + 3})
            i += 4
            continue

        i += 1

    # Phase 2: Simple 2-token patterns (hyphenated, ADJ+NOUN, etc.)
    i = 0
    while i < len(doc) - 1:
        if i in used_indices or i + 1 in used_indices:
            i += 1
            continue

        t1, t2 = doc[i], doc[i + 1]

        # Case: hyphenated word already joined
        if "-" in t1.text and t1.pos_ == "ADJ" and t2.pos_ == "NOUN":
            phrases.append(f"{t1.text.lower()} {t2.text.lower()}")
            used_indices.update({i, i + 1})
            i += 2
            continue

        # Case: known food adjective
        if t1.text.lower() in hyphenated_adjs and t2.pos_ == "NOUN":
            phrases.append(f"{t1.text.lower()} {t2.text.lower()}")
            used_indices.update({i, i + 1})
            i += 2
            continue

        # Case: generic ADJ + NOUN
        if t1.pos_ == "ADJ" and t2.pos_ == "NOUN":
            phrases.append(f"{t1.text.lower()} {t2.text.lower()}")
            used_indices.update({i, i + 1})
            i += 2
            continue

        i += 1

    # Phase 3: Catch remaining standalone NOUNs
    for i, token in enumerate(doc):
        if i not in used_indices and token.pos_ == "NOUN":
            phrases.append(token.text.lower())
            used_indices.add(i)

    return phrases


st.title("Shopping List generator 📃", anchor=False)
st.markdown("---")
st.caption("💡 You can either write or record your list")
container2 = st.container(border= True)

with container2:

    st.subheader("✏️ **Write your grocery list**")
    

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

    st.markdown("---")
    # Friendly heading above the recorder
    st.subheader("🎧 **Record your grocery list**")
    
    # Audio recorder component
    audio = audio_recorder(
        text="Click to Record 👉",          # Button label
        icon_name="microphone",                    
        neutral_color="#00FF00",         # Button color when not recording
        recording_color="#FF0000",       # Button color during recording
        icon_size="1.5x",                  # Icon size (not used since icon_name is empty)
    )
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
                # Step 1: recognise speech
                text = recognizer.recognize_google(audio_data)

                # Step 2: fix multi-word food adjectives like "full fat" → "full-fat"
                text = fix_multiword_adjectives(text)

                # Step 3: show and extract product terms
                st.success(f"🗣️ You said: {text}")
                voice_products = extract_adj_noun_phrases(text)
                st.write("📝 Products from voice:", voice_products)

            except sr.UnknownValueError:
                st.error("❌ Could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"❌ Could not request results; {e}")

    # Combine all product sources
    all_products = list(set(essential_list + voice_products))

container3 = st.container(border=True)

with container3:
    if all_products is not None:
        st.subheader("Product list 🧾")
        st.write("Products List:", all_products)


if "df" in st.session_state and all_products and budget > 0:
    df = st.session_state.df.copy()
    
    # Ensure required columns exist
    if {"Store_Name", "Name", "Price", "Year", "Month", "Day"}.issubset(df.columns):
        df["date"] = pd.to_datetime(df[["Year", "Month", "Day"]])
        
        # Get latest date for each store
        latest_df = df.sort_values("date").groupby("Store").tail(1)
        
        # Filter for required products only
        user_products_lower = [p.lower() for p in all_products]
        latest_df["name_lower"] = latest_df["Name"].str.lower()
        filtered_df = latest_df[latest_df["name_lower"].isin(user_products_lower)]
        
        # Try to build best combo per store
        best_combos = []
        for store, group in filtered_df.groupby("Store_Name"):
            product_map = group.set_index("name_lower")
            
            matched_items = []
            total_price = 0
            
            for prod in user_products_lower:
                if prod in product_map.index:
                    row = product_map.loc[prod]
                    price = row["Price"]
                    total_price += price
                    matched_items.append((row["Name"], price))
            
            if len(matched_items) == len(all_products) and total_price <= budget * 1.1:
                best_combos.append({"Store_Name": store, "Items": matched_items, "Total": total_price})
        
        # Sort by total price and show the best
        best_combos = sorted(best_combos, key=lambda x: x["Total"])
        
        container3.markdown("---")
        container3.subheader("Best deal found 🛍️")

        if best_combos:
            best = best_combos[0]
            container3.success(f"🏪 **Store:** {best['Store_Name']} — 🧾 **Total: £{best['Total']:.2f}**")
            for item, price in best["Items"]:
                container3.markdown(f"- {item}: £{price:.2f}")
        else:
            container3.warning("⚠️ No single store has *all* the requested items within your budget.")
    else:
        container3.error("❌ Dataset is missing required columns.")
else:
    st.info("📌 Please make sure data is loaded, products are entered, and budget is set.")