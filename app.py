import streamlit as st
import json
import datetime
import requests
import random
import os
import re

st.set_page_config(page_title="Scripture Memorizer", layout="centered")

DATA_FILE = "verses.json"
STREAK_FILE = "streak.json"

def rerandomize_blanks():
    v = st.session_state.current_verse
    words = v["text"].split()
    st.session_state.masked_indices = [i for i in range(len(words)) if random.random() < 0.3]
    st.session_state.input_key += 1
    st.experimental_rerun()

def load_new_masked_verse(verses):
    verse = random.choice(verses)
    words = verse["text"].split()
    masked = [i for i in range(len(words)) if random.random() < 0.3]
    return verse, masked

def clean_word(word):
    return re.sub(r'[^\w]', '', word).lower().strip()

def load_verses():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_verses(verses):
    with open(DATA_FILE, 'w') as f:
        json.dump(verses, f, indent=2)

def fetch_verse_from_api(reference):
    url = f"https://bible-api.com/{reference.replace(' ', '%20')}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("text", "").strip()
    else:
        return None

def load_streak():
    if not os.path.exists(STREAK_FILE):
        with open(STREAK_FILE, 'w') as f:
            json.dump({"last_day": str(datetime.date.today()), "streak": 0}, f)
    with open(STREAK_FILE, 'r') as f:
        return json.load(f)

def update_streak():
    data = load_streak()
    today = str(datetime.date.today())
    last_day = data["last_day"]
    if last_day != today:
        delta = (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(last_day)).days
        if delta == 1:
            data["streak"] += 1
        else:
            data["streak"] = 1
        data["last_day"] = today
        with open(STREAK_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    return data["streak"]

# ---------------- UI ----------------

st.title("🕊️ SelahMemory")
st.caption("A quiet place to memorize and meditate on Scripture.")

with st.expander("📚 What's included?"):
    st.markdown("""
**Built-in Memory Sets:**
- 🔹 *Romans Road*: a simple gospel presentation
- 🔹 *Re:generation Steps 1–12*: Scripture tied to the 12-step Christ-centered recovery program

**You can also add your own verses!**
Use the **"Add New"** section to include any passage you'd like to memorize, tag it, and practice it.
    """)

st.sidebar.markdown("### Navigation")
st.sidebar.markdown("---")
st.sidebar.markdown("📚 **Includes:** Roman's Road & Re:generation step memory verses")
st.sidebar.markdown("➕ Add your own verses anytime!")

menu = st.sidebar.radio("Go to", ["View Verses", "Add New", "Practice"])

verses = load_verses()
streak = update_streak()
st.sidebar.success(f"🔥 Streak: {streak} day(s)")

# ---------------- VIEW VERSES ----------------
if menu == "View Verses":
    tag_filter = st.selectbox("Filter by Tag", ["All"] + sorted({tag for v in verses for tag in v.get("tags", [])}))
    filtered = verses if tag_filter == "All" else [v for v in verses if tag_filter in v.get("tags", [])]
    if filtered:
        for v in filtered:
            st.markdown(f"**{v['reference']}** — _{', '.join(v.get('tags', []))}_")
            st.markdown(f"{v['text']}")
            st.markdown(f"_Last Reviewed: {v.get('last_reviewed', 'N/A')}_")
            st.markdown("---")
    else:
        st.info("No verses to show.")

# ---------------- ADD NEW ----------------
elif menu == "Add New":
    with st.form("add_verse"):
        ref = st.text_input("Verse Reference", placeholder="e.g. Romans 8:28")
        use_api = st.checkbox("Auto-fill verse text using Bible API")
        text = ""

        if use_api and ref:
            text = fetch_verse_from_api(ref) or ""
            if text:
                st.text_area("Verse Text (auto-filled)", value=text, height=100)
            else:
                st.error("Could not fetch verse. Check the reference.")
        else:
            text = st.text_area("Verse Text", height=100)

        tags = st.text_input("Tags (comma-separated)", placeholder="e.g. Romans Road, Salvation")
        submit = st.form_submit_button("Add")

        if submit:
            new_verse = {
                "reference": ref,
                "text": text.strip(),
                "status": "learning",
                "last_reviewed": None,
                "tags": [t.strip() for t in tags.split(",") if t.strip()]
            }
            verses.append(new_verse)
            save_verses(verses)
            st.success("Verse added!")

# ---------------- PRACTICE ----------------
elif menu == "Practice":
    if not verses:
        st.info("Add some verses first.")
    else:
        # Initialize session state properly
        if "current_verse" not in st.session_state:
            verse, masked = load_new_masked_verse(verses)
            st.session_state.current_verse = verse
            st.session_state.masked_indices = masked
            st.session_state.input_key = 0

        v = st.session_state.current_verse
        st.markdown(f"### {v['reference']}")
        practice_type = st.radio("Practice Mode", ["Fill in the Blanks", "Type Full Verse"])

        original_words = v["text"].split()

        if practice_type == "Fill in the Blanks":
            # Only generate masked indices once
            if "masked_indices" not in st.session_state or not st.session_state.masked_indices:
                st.session_state.masked_indices = [i for i in range(len(original_words)) if random.random() < 0.3]

            masked_indices = st.session_state.masked_indices

            # Display the verse with blanks
            displayed = [
                "_______" if i in masked_indices else word
                for i, word in enumerate(original_words)
            ]
            st.markdown(" ".join(displayed))

            with st.form(f"fill_in_blanks_{st.session_state.input_key}"):
                user_inputs = []
                for i in masked_indices:
                    key = f"blank_input_{i}"  # Unique key to isolate inputs per word
                    user_word = st.text_input(f"Word #{i+1}", key=key)
                    user_inputs.append((i, user_word.strip()))

                submitted = st.form_submit_button("Check Answers")

            if submitted:
                correct = 0
                for i, user_word in user_inputs:
                    actual = original_words[i]
                    if clean_word(user_word) == clean_word(actual):
                        correct += 1

                st.success(f"{correct} out of {len(masked_indices)} correct.")
                if correct != len(masked_indices):
                    st.markdown("**Correct Verse:**")
                    st.markdown(f"> {v['text']}")

                # Save review date for the current verse
                v["last_reviewed"] = str(datetime.date.today())
                save_verses(verses)

                # ✅ Wait for user to choose to move on
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("🔁 Try Again"):
                        rerandomize_blanks()
                with col2:
                    if st.button("➡️ Next Verse"):
                        st.session_state.current_verse = random.choice(verses)
                        st.session_state.masked_indices = []
                        st.experimental_rerun()

        elif practice_type == "Type Full Verse":
            user_input = st.text_area("Type the verse from memory:")
            if st.button("Check"):
                if clean_word(user_input) == clean_word(v["text"]):
                    st.success("Correct! 🎉")
                else:
                    st.error("Not quite. Keep practicing!")
                    st.markdown(f"**Correct verse:** {v['text']}")

                v["last_reviewed"] = str(datetime.date.today())
                save_verses(verses)
                st.session_state.current_verse = random.choice(verses)
                st.session_state.masked_indices = []  # Reset
