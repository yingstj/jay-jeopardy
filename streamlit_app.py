import streamlit as st
import pandas as pd
import random
import datetime
import boto3
import io

# Function to load data from R2
def load_jeopardy_data_from_r2():
    try:
        # Create S3 client for R2
        s3_client = boto3.client(
            's3',
            endpoint_url=st.secrets.get("R2_ENDPOINT_URL", "https://7273c297879bcf94573d10e2b8bbfc7a.r2.cloudflarestorage.com"),
            aws_access_key_id=st.secrets.get("R2_ACCESS_KEY", "9c27eeaf6574bd7c80915531337fc15c"),
            aws_secret_access_key=st.secrets.get("R2_SECRET_KEY", "db3cc4453aa7ada3764653206bb43a3a4185988271d90aae277aed2eb8514050")
        )
        
        # Download the file from R2
        bucket_name = st.secrets.get("R2_BUCKET_NAME", "jeopardy-dataset")
        file_key = st.secrets.get("R2_FILE_KEY", "all_jeopardy_clues.csv")
        
        st.info(f"Attempting to load data from R2 bucket: {bucket_name}")
        
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        data = response['Body'].read()
        
        # Load into pandas
        df = pd.read_csv(io.BytesIO(data))
        
        # Convert DataFrame to list of dictionaries
        clues = df.to_dict(orient="records")
        
        st.success(f"Successfully loaded {len(clues)} clues from R2!")
        return clues
        
    except Exception as e:
        st.error(f"Error loading data from R2: {e}")
        # Fall back to sample data
        return sample_data

# Sample data for fallback
sample_data = [
    {"category": "HISTORY", "clue": "First president of the US", "correct_response": "George Washington"},
    {"category": "SCIENCE", "clue": "Element with symbol H", "correct_response": "Hydrogen"},
    {"category": "MOVIES", "clue": "This film won Best Picture in 2020", "correct_response": "Parasite"},
    {"category": "GEOGRAPHY", "clue": "Largest ocean on Earth", "correct_response": "Pacific Ocean"},
    {"category": "LITERATURE", "clue": "Author of 'To Kill a Mockingbird'", "correct_response": "Harper Lee"},
    {"category": "SPORTS", "clue": "Number of players on a standard soccer team", "correct_response": "11"}
]

st.title("🧠 Jay's Jeopardy Trainer")

# Try to load data from R2
with st.spinner("Loading Jeopardy dataset..."):
    jeopardy_data = load_jeopardy_data_from_r2()

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

if "score" not in st.session_state:
    st.session_state.score = 0
    st.session_state.total = 0

if "current_clue" not in st.session_state:
    st.session_state.current_clue = random.choice(jeopardy_data)
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

    st.session_state.current_clue = random.choice(jeopardy_data)
    st.rerun()  # Fixed: Changed from st.experimental_rerun()

# Display score
if st.session_state.total:
    st.markdown("---")
    st.metric("Your Score", f"{st.session_state.score} / {st.session_state.total}")

# Display history
if st.session_state.history:
    st.subheader("📊 Session Recap")
    st.dataframe(pd.DataFrame(st.session_state.history))
