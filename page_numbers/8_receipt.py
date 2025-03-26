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

    if "voice_products" not in st.session_state:
        st.session_state.voice_products = []

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
                new_voice_products = extract_adj_noun_phrases(text)
                # Avoid duplicates and add only new items
                for item in new_voice_products:
                    if item not in st.session_state.voice_products:
                        st.session_state.voice_products.append(item)

            except sr.UnknownValueError:
                st.error("❌ Could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"❌ Could not request results; {e}")

    # Combine all product sources
    all_products = list(set(essential_list + st.session_state.voice_products))

container3 = st.container(border=True)

# Keep previous product list for comparison
if "prev_products" not in st.session_state:
    st.session_state.prev_products = []

# Check if the product list has changed
if set(all_products) != set(st.session_state.prev_products):
    st.session_state.finalised = False
    st.session_state.prev_products = all_products.copy()
with container3:
    st.subheader("🧾 Product List")

    if all_products:
        st.markdown("Here are your selected items (tick to delete):")
        
        # Initialise checkbox states if not done already
        if "delete_flags" not in st.session_state or len(st.session_state.delete_flags) != len(all_products):
            st.session_state.delete_flags = [False] * len(all_products)

        # Display with checkboxes
        for idx, product in enumerate(all_products):
            st.session_state.delete_flags[idx] = st.checkbox(
                label=f"{idx + 1}. {product}",
                key=f"delete_{idx}",
                value=st.session_state.delete_flags[idx]
            )

        # Delete button
        if st.button("🗑️ Delete Selected", use_container_width=True):
            items_to_delete = [
                product for idx, product in enumerate(all_products)
                if st.session_state.delete_flags[idx]
            ]

            # Remove from both sources (voice + essential)
            st.session_state.voice_products = [
                item for item in st.session_state.voice_products if item not in items_to_delete
            ]
            essential_list = [
                item for item in essential_list if item not in items_to_delete
            ]

            # Rebuild product list
            all_products = list(set(essential_list + st.session_state.voice_products))
            st.session_state.prev_products = all_products.copy()
            st.session_state.finalised = False
            st.success("Selected items deleted.")

            # Reset checkbox flags
            st.session_state.delete_flags = [False] * len(all_products)

    else:
        st.info("No products selected.")

    # Finalise button logic
    if not st.session_state.finalised and all_products:
        if st.button("✅ Finalise List", use_container_width=True):
            st.session_state.finalised = True
            st.success("List has been finalised.")
    elif st.session_state.finalised:
        st.success("✅ This list has already been finalised.")


if "df" in st.session_state and all_products and budget > 0:
    pass

    