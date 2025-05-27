import streamlit as st
import json
import datetime

DATA_FILE = "verses.json"

# Load/save helpers
def load_verses():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_verses(verses):
    with open(DATA_FILE, 'w') as f:
        json.dump(verses, f, indent=2)

# Add verse
def add_verse(reference, text):
    verses = load_verses()
    verses.append({
        "reference": reference,
        "text": text,
        "last_reviewed": str(datetime.date.today())
    })
    save_verses(verses)

# UI starts here
st.title("📖 Scripture Memorizer")

menu = st.sidebar.selectbox("Menu", ["View Verses", "Add New", "Practice"])

if menu == "View Verses":
    verses = load_verses()
    if verses:
        for v in verses:
            st.markdown(f"**{v['reference']}**\n\n{v['text']}\n\n_Last Reviewed: {v['last_reviewed']}_")
            st.markdown("---")
    else:
        st.info("No verses saved yet.")

elif menu == "Add New":
    with st.form("add_verse"):
        ref = st.text_input("Verse Reference", placeholder="e.g. John 3:16")
        text = st.text_area("Verse Text", height=100)
        submit = st.form_submit_button("Add")
        if submit:
            add_verse(ref, text)
            st.success("Verse added!")

elif menu == "Practice":
    verses = load_verses()
    if not verses:
        st.info("Add some verses first.")
    else:
        import random
        v = random.choice(verses)
        st.markdown(f"**{v['reference']}**")
        practice_type = st.radio("Practice Mode", ["Hide Some Words", "Type Full Verse"])

        if practice_type == "Hide Some Words":
            words = v["text"].split()
            masked = [w if random.random() > 0.3 else "_____" for w in words]
            st.markdown(" ".join(masked))

        elif practice_type == "Type Full Verse":
            user_input = st.text_area("Type the verse from memory:")
            if st.button("Check"):
                if user_input.strip().lower() == v["text"].strip().lower():
                    st.success("Correct! 🎉")
                else:
                    st.error("Not quite. Keep practicing!")
                    st.markdown(f"**Correct verse:** {v['text']}")

        # Update last reviewed date
        v["last_reviewed"] = str(datetime.date.today())
        save_verses(verses)
