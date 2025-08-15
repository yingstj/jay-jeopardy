import streamlit as st
import pandas as pd
import random
import datetime

# Sample data for testing - replace with your actual data loading later
sample_data = [
    {"category": "HISTORY", "clue": "First president of the US", "correct_response": "George Washington"},
    {"category": "SCIENCE", "clue": "Element with symbol H", "correct_response": "Hydrogen"},
    {"category": "MOVIES", "clue": "This film won Best Picture in 2020", "correct_response": "Parasite"},
    {"category": "GEOGRAPHY", "clue": "Largest ocean on Earth", "correct_response": "Pacific Ocean"},
    {"category": "LITERATURE", "clue": "Author of 'To Kill a Mockingbird'", "correct_response": "Harper Lee"},
    {"category": "SPORTS", "clue": "Number of players on a standard soccer team", "correct_response": "11"}
]

st.title("🧠 Jay's Jeopardy Trainer")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

if "score" not in st.session_state:
    st.session_state.score = 0
    st.session_state.total = 0

if "current_clue" not in st.session_state:
    st.session_state.current_clue = random.choice(sample_data)
    st.session_state.start_time = datetime.datetime.now()

# Display current clue
clue = st.session_state.current_clue
st.subheader(f"📚 Category: {clue['category']}")
st.markdown(f"**Clue:** {clue['clue']}")

# Get user response
with st.form(key="clue_form"):
    user_input = st.text_input("Your response:")
    submitted = st.form_submit_button("Submit")

if submitted:
    user_clean = user_input.lower().strip()
    answer_clean = clue["correct_response"].lower().strip()
    correct = user_clean == answer_clean

    if correct:
        st.success("✅ Correct!")
        st.session_state.score += 1
    else:
        st.error(f"❌ Incorrect. The correct response was: *{clue['correct_response']}*")

    st.session_state.total += 1
    st.session_state.history.append({
        "category": clue["category"],
        "clue": clue["clue"],
        "correct_response": clue["correct_response"],
        "user_response": user_input,
        "was_correct": correct
    })

    st.session_state.current_clue = random.choice(sample_data)
    st.experimental_rerun()

# Display score
if st.session_state.total:
    st.markdown("---")
    st.metric("Your Score", f"{st.session_state.score} / {st.session_state.total}")

# Display history
if st.session_state.history:
    st.subheader("📊 Session Recap")
    st.dataframe(pd.DataFrame(st.session_state.history))
