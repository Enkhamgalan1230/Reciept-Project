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

# ========== SESSION STATE SETUP ==========
if "df" in st.session_state:
    df = st.session_state.df
else:
    st.warning("💡 Hint: No data available. Please visit the Data Fetcher page quickly and come back to this page.")

for key in ["essential_list", "voice_products", "all_products"]:
    if key not in st.session_state:
        st.session_state[key] = []

# ========== LOAD MODELS AND DATA ==========
nlp = spacy.load("en_core_web_sm")
df_adj = pd.read_csv("food_adjectives.csv")
hyphenated_adjs = set(df_adj["Food_Adjective"].str.lower().tolist())
phrase_map = {adj.replace("-", " "): adj for adj in hyphenated_adjs}

# ========== TEXT PROCESSING HELPERS ==========
def fix_multiword_adjectives(text):
    for plain, hyphenated in phrase_map.items():
        if plain in text:
            text = text.replace(plain, hyphenated)
    return text

def extract_adj_noun_phrases(text):
    doc = nlp(text)
    phrases = []
    used_indices = set()

    i = 0
    while i < len(doc) - 3:
        t1, t2, t3, t4 = doc[i], doc[i+1], doc[i+2], doc[i+3]
        if t1.pos_ == "ADJ" and t2.text == "-" and t4.pos_ == "NOUN":
            hyphenated = f"{t1.text.lower()}-{t3.text.lower()}"
            phrases.append(f"{hyphenated} {t4.text.lower()}")
            used_indices.update({i, i+1, i+2, i+3})
            i += 4
            continue
        i += 1

    i = 0
    while i < len(doc) - 1:
        if i in used_indices or i+1 in used_indices:
            i += 1
            continue
        t1, t2 = doc[i], doc[i+1]
        if "-" in t1.text and t1.pos_ == "ADJ" and t2.pos_ == "NOUN":
            phrases.append(f"{t1.text.lower()} {t2.text.lower()}")
        elif t1.text.lower() in hyphenated_adjs and t2.pos_ == "NOUN":
            phrases.append(f"{t1.text.lower()} {t2.text.lower()}")
        elif t1.pos_ == "ADJ" and t2.pos_ == "NOUN":
            phrases.append(f"{t1.text.lower()} {t2.text.lower()}")
        else:
            i += 1
            continue
        used_indices.update({i, i+1})
        i += 2

    for i, token in enumerate(doc):
        if i not in used_indices and token.pos_ == "NOUN":
            phrases.append(token.text.lower())
            used_indices.add(i)

    return phrases

# ========== UI ==========
st.title("Shopping List generator 📃", anchor=False)
st.caption("💡 You can either write or record your list")
st.markdown("---")

st.markdown("""
    <style>
        .custom-container {
            background-color: #2b2b2b;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ========== MANUAL ENTRY ==========
container1 = st.container(border= True)
container2 = st.container(border= True)
container3 = st.container(border= True)

with container1:
    st.subheader("✏️ Write your grocery list")
    budget = st.number_input("Insert the budget (£)", placeholder="Ex: 30", format="%0.2f", min_value=0.0)

    with st.form("add_item_form"):
        new_item = st.text_input("Add an item to the list")
        submitted = st.form_submit_button("➕ Add Item")
        if submitted:
            clean_item = new_item.strip().lower()
            if clean_item and clean_item not in st.session_state.essential_list:
                st.session_state.essential_list.append(clean_item)
                st.success(f"Added '{clean_item}'")
                st.rerun()
            elif clean_item:
                st.warning("Item already in the list.")


# ========== VOICE INPUT ==========
with container2:
    st.subheader("🗣️ **Speak your grocery list**")
    st.markdown("---")
    audio = audio_recorder(
        text="Click to Record 👉",
        icon_name="microphone",
        neutral_color="#00FF00",
        recording_color="#FF0000",
        icon_size="1.5x"
    )

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
                text = fix_multiword_adjectives(text)
                st.success(f"🗣️ You said: {text}")
                new_voice_products = extract_adj_noun_phrases(text)
                for item in new_voice_products:
                    clean_item = item.strip("'\"").strip().lower()
                    if clean_item not in st.session_state.voice_products:
                        st.session_state.voice_products.append(clean_item)
            except sr.UnknownValueError:
                st.error("❌ Could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"❌ Could not request results; {e}")

# ========== COMBINED PRODUCT LIST ==========
st.session_state.all_products = (
    st.session_state.essential_list + st.session_state.voice_products
)

with container3:
    st.subheader("🧾 **Combined Grocery List**")
    if st.session_state.all_products:

        to_delete_flags = {}

        for idx, item in enumerate(st.session_state.all_products, start=1):
            label = f"{idx}. {item.title()}"
            to_delete_flags[item] = st.checkbox(label, key=f"delete_{item}")

        st.markdown(" ")
        if st.button("🗑️ Delete Selected Items", use_container_width=True):
            selected_to_delete = [item for item, selected in to_delete_flags.items() if selected]

            st.session_state.essential_list = [
                item for item in st.session_state.essential_list if item not in selected_to_delete
            ]
            st.session_state.voice_products = [
                item for item in st.session_state.voice_products if item not in selected_to_delete
            ]
            st.session_state.all_products = [
                item for item in st.session_state.all_products if item not in selected_to_delete
            ]

            st.success("Selected item(s) deleted.")
            st.rerun()
    else:
        st.info("Your list is currently empty.")
st.caption("📌 Selected items can be deleted from the list")

final_list = list(dict.fromkeys(st.session_state.all_products))

