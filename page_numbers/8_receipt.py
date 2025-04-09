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
import hashlib
import openai
from groq import Groq
import re

# Check if df is stored in session state
if "df" in st.session_state:
    df = st.session_state.df  # Retrieve stored data
else:
    st.warning("💡 Hint: No data available. Please visit the Data Fetcher page quickly and come back to this page.")

# Set your Groq API Key
# Initialise client using Streamlit Secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

system_prompt = (
    "You are a helpful assistant for a grocery list app. "
    "When the user asks about what to buy, first explain the reasoning behind your suggestions. "
    "Then, provide a separate section titled 'Suggested items:' followed by a markdown bullet-point list of **only grocery item names** (no quantities or extra notes). "
    "Avoid non-food items unless specifically asked."
)

# ========== SESSION STATE SETUP ==========
for key in ["essential_list", "voice_products", "secondary_list"]:
    if key not in st.session_state:
        st.session_state[key] = []

if "audio_processed" not in st.session_state:
    st.session_state.audio_processed = False

if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ========== LOAD MODELS AND DATA ==========
@st.cache_resource
def load_nlp_model():
    return spacy.load("en_core_web_sm")

@st.cache_data
def load_adjectives():
    df = pd.read_csv("food_adjectives.csv")
    hyphens = set(df["Food_Adjective"].str.lower().tolist())
    return hyphens, {adj.replace("-", " "): adj for adj in hyphens}

def clean_transcript(text):
    filler_phrases = [
        "add to my shopping list",
        "add this to my shopping list",
        "to my shopping list",
        "add to the list",
        "add this",
        "can you add",
        "please add",
        "i want",
        "i would like",
        "put",
        "include"
    ]

    text = text.lower()
    for phrase in filler_phrases:
        if phrase in text:
            text = text.replace(phrase, "")
    return text.strip()

nlp = load_nlp_model()
hyphenated_adjs, phrase_map = load_adjectives()

# ========== TEXT PROCESSING HELPERS ==========
def extract_bullet_items(text):
    # Find the section after "Suggested items:"
    split_text = re.split(r"(?i)suggested items:?", text)  # case-insensitive
    if len(split_text) < 2:
        return []  # No list section found

    list_block = split_text[1]
    lines = list_block.strip().splitlines()

    items = []
    for line in lines:
        match = re.match(r"^\s*[-*•]\s*(.+)", line)
        if match:
            items.append(match.group(1).strip())
        else:
            break  # Stop at first non-bullet line

    return items

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
st.title("Shopping List generator 📃")
st.caption("💡 You can either write or record your list")
st.markdown("---")

# ========== MANUAL ENTRY ==========
container1 = st.container(border=True)
container2 = st.container(border=True)
container3 = st.container(border=True)
container4 = st.container(border=True)

with container1:
    st.subheader("✏️ **Write your grocery list**")
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

    with st.form("add_secondary_form"):
        new_item = st.text_input("I would love to include this if we can..")
        submitted = st.form_submit_button("➕ Add Item")
        if submitted:
            clean_item = new_item.strip().lower()
            if clean_item and clean_item not in st.session_state.secondary_list:
                st.session_state.secondary_list.append(clean_item)
                st.success(f"Added '{clean_item}'")
                st.rerun()
            elif clean_item:
                st.warning("Item already in the list.")

# ========== VOICE INPUT ==========
# In the VOICE INPUT section:

def get_audio_hash(audio_bytes):
    return hashlib.md5(audio_bytes).hexdigest()

with container2:
    st.subheader("🗣️ **Speak your grocery list**")

    audio = audio_recorder(
        text="Click to Record 👉",
        icon_name="microphone",
        neutral_color="#00FF00",
        recording_color="#FF0000",
        icon_size="1.5x"
    )

    # Placeholder to show transcript *immediately after mic button*
    latest_transcript = st.session_state.transcribed_text
    transcript_placeholder = st.empty()  # Reserve the space for text

    if audio:
        current_hash = get_audio_hash(audio)

        if st.session_state.get("last_audio_hash") != current_hash:
            st.session_state.last_audio_hash = current_hash

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio)
                temp_path = f.name

            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_path) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data)
                    text = clean_transcript(text)
                    text = fix_multiword_adjectives(text)

                    st.session_state.transcribed_text = text
                    latest_transcript = text  # ✅ Update immediately

                    new_items = extract_adj_noun_phrases(text)
                    for item in new_items:
                        clean = item.strip("'\"").strip().lower()
                        if clean not in st.session_state.voice_products:
                            st.session_state.voice_products.append(clean)

                except sr.UnknownValueError:
                    transcript_placeholder.error("❌ Could not understand the audio.")
                except sr.RequestError as e:
                    transcript_placeholder.error(f"❌ Could not request results; {e}")

            st.audio(audio, format="audio/wav")  # 👈 Still show the player after processing

    # Always display latest transcript just under mic
    if latest_transcript:
        transcript_placeholder.success(f"🗣️ You said: {latest_transcript}")

# Optional: Reset flags if no audio
if audio is None:
    st.session_state.audio_processed = False

with container3:
    st.subheader("🧠 AI Shopping Assistant")
    # Input field
    user_query = st.text_input("Ask me what to cook or what to buy:", key="chat_query")

    # Ask button
    if st.button("🧠 Ask"):
        if user_query:
            st.session_state.chat_history.append({"role": "user", "content": user_query})

            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *st.session_state.chat_history
                    ],
                    temperature=0.4,
                    max_tokens=600
                )

                bot_reply = response.choices[0].message.content
                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
                st.session_state.last_bot_reply = bot_reply

    # Display latest assistant message
    if "last_bot_reply" in st.session_state:
        st.markdown("##### 📝 Assistant's Response")
        st.markdown(st.session_state.last_bot_reply)

        # Finalise button
        if st.button("✅ Add to Grocery List"):
            extracted_items = re.findall(r"[-*•]\s*(.+)", st.session_state.last_bot_reply)
            added_items = 0
            for item in extracted_items:
                clean = item.strip().lower()
                if clean not in st.session_state.essential_list:
                    st.session_state.essential_list.append(clean)
                    added_items += 1
            st.success(f"✅ {added_items} item(s) added to your grocery list.")

    with st.expander("💬 View Chat History"):
        for entry in st.session_state.chat_history:
            role = "👤 You" if entry["role"] == "user" else "🤖 Assistant"
            st.markdown(f"**{role}:** {entry['content']}")

# ========== COMBINED LIST ==========
all_products = st.session_state.essential_list + st.session_state.voice_products
secondary_products = st.session_state.secondary_list


with container4:
    st.subheader("🧾 **Combined Grocery List**")

    if st.session_state.get("show_delete_toast"):
        st.toast("✅ Selected primary item(s) deleted.")
        del st.session_state["show_delete_toast"]
    
    if st.session_state.get("show_delete_secondary_toast"):
        st.toast("✅ Selected secondary item(s) deleted.")
        del st.session_state["show_delete_secondary_toast"]

    # Essential + Voice Products
    if all_products:
        st.caption("✅ Tick items to delete from your primary list")
        to_delete_flags = {}

        for idx, item in enumerate(all_products, start=1):
            label = f"{idx}. {item.title()}"
            to_delete_flags[item] = st.checkbox(label, key=f"delete_{item}")

        if st.button("🗑️ Delete Selected Primary Items", key="delete_primary", use_container_width=True):
            selected_to_delete = [item for item, selected in to_delete_flags.items() if selected]

            st.session_state.essential_list = [
                item for item in st.session_state.essential_list if item not in selected_to_delete
            ]
            st.session_state.voice_products = [
                item for item in st.session_state.voice_products if item not in selected_to_delete
            ]
            st.session_state["show_delete_toast"] = True
            st.rerun()
    else:
        st.info("Your primary list is currently empty.")

    st.markdown("---")

    # Secondary List
    st.subheader("✨ Optional Extras (Secondary List)")

    if secondary_products:
        st.caption("These are the items you'd like to include *if budget allows*. You can also remove them below.")
        to_delete_secondary = {}

        for idx, item in enumerate(secondary_products, start=1):
            label = f"{idx}. {item.title()}"
            to_delete_secondary[item] = st.checkbox(label, key=f"delete_secondary_{item}")

        if st.button("🗑️ Delete Selected Secondary Items", key="delete_secondary", use_container_width=True):
            selected_to_delete = [item for item, selected in to_delete_secondary.items() if selected]

            st.session_state.secondary_list = [
                item for item in st.session_state.secondary_list if item not in selected_to_delete
            ]
            st.session_state["show_delete_secondary_toast"] = True
            st.rerun()
            
    else:
        st.info("No secondary items added yet.")

