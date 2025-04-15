# ========== IMPORTS ==========

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
from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
#from sentence_transformers import SentenceTransformer
# ========== SESSION STATE SETUP ==========

# Check if df is stored in session state
if "df" in st.session_state:
    df = st.session_state.df  # Retrieve stored data
else:
    st.warning("💡 Hint: No data available. Please visit the Data Fetcher page quickly and come back to this page.")

# Set up Groq API Key
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

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
exclude_keywords = [
    # Dietary substitutes / labels
    "vegan", "vegetarian", "plant-based", "plant", "meat-free", "meat alternative",
    "non-dairy", "dairy-free", "egg-free", "gluten-free", "free from",

    # Prepared / cooked / processed items
    "ready", "ready meal", "frozen meal", "pre-cooked", "precooked", "cooked",
    "marinated", "roast", "roasted", "grilled", "tandoori", "bbq", "barbecue",
    "fried", "battered", "smoked", "steamed", "seasoned", "cured","frozen", "breaded",
    "cure","joint","stuffing"

    # Flavourings and sweet/dessert items
    "flavoured", "flavor", "sweet", "dessert", "chocolate", "vanilla", "caramel",

    # Packaged and processed variations
    "sliced", "shredded", "deli", "nugget", "burger", "sausage", "bacon", "balls",
    "bites", "strips", "patties", "chunks", "goujon", "finger", "popcorn",

    # Canned and jarred goods
    "canned", "tinned", "jar", "paste", "spread", "puree",

    # Beverages and liquids
    "drink", "smoothie", "juice", "shake", "beverage", "milkshake", "infused",

    # Snacks and side products
    "snack", "bar", "crisp", "chip", "popcorn", "dip", "sauce", "gravy", "dressing",

    # Substitutes and alternatives
    "substitute", "alternative", "replacement", "replica", "mock", "fake", "faux",
    
    # Other ambiguous types
    "baby", "pet", "cat", "dog", "kitten", "puppy", "feed", "food for", "food supplement",
]


system_prompt = (
    "You are a helpful assistant for a grocery list app and your name is Entwan. "
    "When the user asks about what to buy, first introduce your name and explain the reasoning behind your suggestions. "
    "Then, provide a separate section titled 'Suggested items:' followed by a markdown bullet-point list of **only grocery item names** (no quantities or extra notes) also don't offer item. "
    "Avoid non-food items unless specifically asked."
    "Avoid using alternatives or slashes like 'or', '/', or parentheses. Always choose one clear, specific item to recommend in the grocery list."
)

nlp = load_nlp_model()
hyphenated_adjs, phrase_map = load_adjectives()


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

def get_audio_hash(audio_bytes):
    return hashlib.md5(audio_bytes).hexdigest()



def is_excluded(product_name):
    name = product_name.lower()
    return any(keyword in name for keyword in exclude_keywords)

def is_match(user_input, product_name):
    user_input = user_input.lower().strip()
    product_name = product_name.lower().strip()

    # Word-boundary match
    return re.search(rf"\b{re.escape(user_input)}\b", product_name) is not None

def get_matching_items(user_item, df):
    matches = df[df["Name"].apply(lambda name: is_match(user_item, name) and not is_excluded(name))]
    matches = matches.sort_values(by="Price")
    return matches

def get_cheapest_items(items, df, store, budget):
    selected_items = []
    total_cost = 0.0

    for item in items:
        matches = get_matching_items(item, df[df["Store_Name"] == store])

        if not matches.empty:
            cheapest = matches.iloc[0]
            item_price = cheapest["Price"]

            if total_cost + item_price <= budget:
                selected_items.append(cheapest)
                total_cost += item_price
            else:
                break

    return selected_items, total_cost

def add_secondary_items(secondary_items, df, store, current_cost, budget):
    added_items = []

    for item in secondary_items:
        matches = get_matching_items(item, df[df["Store_Name"] == store])
        if not matches.empty:
            cheapest = matches.iloc[0]
            price = cheapest["Price"]

            if current_cost + price <= budget:
                added_items.append(cheapest)
                current_cost += price
            else:
                continue

    return added_items, current_cost

# ========== Main File ==========
st.title("Shopping List generator 📃")
st.caption("💡 You can write, speak or generate your shopping list here!")
st.markdown("---")

# I like containers haha.
container1 = st.container(border=True)
container2 = st.container(border=True)
container3 = st.container(border=True)
container4 = st.container(border=True)

# ========== WRITING INPUT ==========
with container1:
    st.subheader("✏️ **Write your grocery list**")
    st.caption("📌 If you know what you are buying, write it up here...")
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

with container2:
    st.subheader("🗣️ **Speak your grocery list**")
    st.caption("📌 Writing is boring IK, speak it here...")

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
                    latest_transcript = text  # Update immediately

                    new_items = extract_adj_noun_phrases(text)
                    for item in new_items:
                        clean = item.strip("'\"").strip().lower()
                        if clean not in st.session_state.voice_products:
                            st.session_state.voice_products.append(clean)

                except sr.UnknownValueError:
                    transcript_placeholder.error("❌ Could not understand the audio.")
                except sr.RequestError as e:
                    transcript_placeholder.error(f"❌ Could not request results; {e}")

            st.audio(audio, format="audio/wav")  # Still show the player after processing

    # Always display latest transcript just under mic
    if latest_transcript:
        transcript_placeholder.success(f"🗣️ You said: {latest_transcript}")

# Optional: Reset flags if no audio
if audio is None:
    st.session_state.audio_processed = False

# ========== AI INPUT ==========
with container3:
    st.subheader("🧠 AI Shopping Assistant")
    st.caption("📌 If you don't know what to buy, explain it to AI...")
    # Input field
    user_query = st.text_input("Ask me what to cook or what to buy:", key="chat_query")

    # Ask button
    if st.button("Ask"):
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
        if st.button("Add to Grocery List"):
            extracted_items = re.findall(r"^\s*[-*•]\s*(.+)", st.session_state.last_bot_reply, flags=re.MULTILINE)

            # Strip formatting and remove 'Suggested items' safely
            cleaned_items = []
            for item in extracted_items:
                plain = re.sub(r"[*_`]", "", item.strip().lower())  # remove markdown
                if plain != "suggested items":
                    cleaned_items.append(item.strip())

            added_items = 0
            for item in cleaned_items:
                clean = item.strip().lower()
                if clean and clean not in st.session_state.essential_list:
                    st.session_state.essential_list.append(clean)
                    added_items += 1

            if added_items:
                st.success(f"✅ {added_items} item(s) added to your grocery list.")
            else:
                st.warning("⚠️ No valid items found to add.")

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

# Combine year, month, and day into a datetime column
df["Date"] = pd.to_datetime(df[["Year", "Month", "Day"]])

# Get the most recent date
latest_date = df["Date"].max()

# Filter to only the rows with the latest date
latest_df = df[df["Date"] == latest_date]

st.write(latest_df)
options = ["Tesco", "Waitrose", "Asda", "Aldi", "Sainsburys"]
selection = st.pills("Stores", options, selection_mode="single")

essential_items = st.session_state.essential_list
secondary_items = st.session_state.secondary_list


if st.button("🛒 Generate List"):
    if not essential_items:
        st.warning("⚠️ Your essential item list is empty. Please add at least one item.")
    else:
        budget = st.session_state.get("budget", 20.0)
        store = selection

        store_df = latest_df[latest_df["Store_Name"] == store]

        essential_result, cost = get_cheapest_items(essential_items, store_df, store, budget)
        secondary_result, final_cost = add_secondary_items(secondary_items, store_df, store, cost, budget)

        final_items = essential_result + secondary_result

        if final_items:
            result_df = pd.DataFrame(final_items)
            result_df = result_df[["Name", "Price", "Store_Name", "Category", "Subcategory"]]
            st.subheader("✅ Final Shopping List")
            st.dataframe(result_df, use_container_width=True)
            st.success(f"🧮 Total Cost: £{final_cost:.2f} out of £{budget:.2f}")
        else:
            st.warning("⚠️ None of the items fit within your budget.")