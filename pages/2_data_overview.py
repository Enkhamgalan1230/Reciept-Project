import streamlit as st
import mysql.connector
import pandas as pd
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import time
import random

st.title("📊 Data")

# Initialize Supabase connection
conn = st.connection("supabase", type=SupabaseConnection)

# Ensure data is only fetched once
if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.data_fetched = False  # Flag to track if data was already fetched

# Initialize game session state (only if not set)
if "target_number" not in st.session_state:
    st.session_state.target_number = random.randint(1, 100)
    st.session_state.attempts_left = 5
    st.session_state.game_message = "Guess a number between 1 and 100!"
    st.session_state.game_over = False

# Function to play Number Guessing Game
def play_number_guessing_game():
    st.subheader("🎮 Number Guessing Game")
    st.write(f"🔢 Attempts Left: {st.session_state.attempts_left}")

    # Preserve message color formatting using HTML
    st.markdown(st.session_state.game_message, unsafe_allow_html=True)

    user_guess = st.number_input("Enter your guess:", min_value=1, max_value=100, step=1, key="guess_input")

    if st.button("Submit Guess", key="submit_guess"):
        if st.session_state.attempts_left > 0 and not st.session_state.game_over:
            if user_guess == st.session_state.target_number:
                st.session_state.game_message = '<p style="background-color:#007BFF; color:white; padding:10px; border-radius:5px;">🎉 Correct! You guessed the number!</p>'
                st.session_state.game_over = True  # Game over
            elif user_guess > st.session_state.target_number:
                st.session_state.game_message = '<p style="background-color:#28A745; color:white; padding:10px; border-radius:5px;">🔼 Too High! Try again.</p>'
            else:
                st.session_state.game_message = '<p style="background-color:#DC3545; color:white; padding:10px; border-radius:5px;">🔽 Too Low! Try again.</p>'

            st.session_state.attempts_left -= 1  # Reduce attempts

        if st.session_state.attempts_left == 0 and user_guess != st.session_state.target_number:
            st.session_state.game_message = f'<p style="background-color:#DC3545; color:white; padding:10px; border-radius:5px;">😢 Game Over! The number was {st.session_state.target_number}.</p>'
            st.session_state.game_over = True

        st.rerun()  # Rerun only for game updates

    # Play Again Button (resets only the game)
    if st.session_state.game_over:
        if st.button("🔄 Play Again", key="play_again"):
            st.session_state.target_number = random.randint(1, 100)
            st.session_state.attempts_left = 5
            st.session_state.game_message = "Guess a number between 1 and 100!"
            st.session_state.game_over = False
            st.rerun()  # Only restart the game, not fetch data

# Fetch data only once
if not st.session_state.data_fetched:
    @st.cache_data  # Cache the fetched data
    def fetch_data():
        try:
            row_count_result = conn.table("Product").select("*", count="exact", head=True).execute()
            max_rows = row_count_result.count
            st.write(f"There are {max_rows} rows currently in the database.")
            st.write("There is a 1000-row limit per request, so fetching will take some time. 😊")

            batch_size = 1000
            total_batches = (max_rows + batch_size - 1) // batch_size  

            progress_bar = st.progress(0)  
            progress_text = st.empty()  

            all_rows = []
            offset = 0

            for batch in range(1, total_batches + 1):
                try:
                    rows = conn.table("Product").select("*").range(offset, offset + batch_size - 1).execute()

                    if not rows.data:
                        break

                    all_rows.extend(rows.data)
                    offset += batch_size

                    # Update progress bar
                    progress_percentage = batch / total_batches
                    progress_bar.progress(min(progress_percentage, 1.0))

                    # Update progress text
                    progress_text.write(f"Fetching batch {batch}/{total_batches}...")

                    time.sleep(0.5)  # Simulate delay

                except Exception as e:
                    st.write(f"Error at batch {batch}, offset {offset}: {e}")
                    break

            df = pd.DataFrame(all_rows)
            st.write("✅ Data fetching completed!")
            return df

        except Exception as e:
            st.write(f"Error fetching data: {e}")
            return None

    # Show game while loading
    if not st.session_state.data_fetched:
        play_number_guessing_game()

    # Fetch and store in session state
    df = fetch_data()
    st.session_state.df = df  
    st.session_state.data_fetched = True  # Mark as fetched to prevent re-fetching

# Display fetched data
if st.session_state.df is not None:
    st.write("✅ Data loaded successfully!")
    st.dataframe(st.session_state.df.head())  
else:
    st.write("⚠️ No data available.")