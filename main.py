import json

def load_verses(filename='verses.json'):
    with open(filename, 'r') as f:
        return json.load(f)

def save_verses(verses, filename='verses.json'):
    with open(filename, 'w') as f:
        json.dump(verses, f, indent=2)

def add_verse():
    ref = input("Enter verse reference (e.g., John 3:16): ")
    text = input("Enter verse text: ")
    verses = load_verses()
    verses.append({
        "reference": ref,
        "text": text,
        "status": "learning",
        "last_reviewed": None
    })
    save_verses(verses)
    print(f"Added {ref}")

def show_all():
    verses = load_verses()
    for v in verses:
        print(f"{v['reference']}: {v['text']}")

# Example usage
add_verse()
show_all()
