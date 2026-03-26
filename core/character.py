import json
import os

CHARACTERS_DIR = "characters"

def ensure_characters_dir():
    if not os.path.exists(CHARACTERS_DIR):
        os.makedirs(CHARACTERS_DIR)

def save_character(character):
    ensure_characters_dir()
    filepath = os.path.join(CHARACTERS_DIR, f"{character['name'].lower()}.json")
    with open(filepath, "w") as f:
        json.dump(character, f, indent=4)
    print(f"Character '{character['name']}' saved!")

def load_character(name):
    filepath = os.path.join(CHARACTERS_DIR, f"{name.lower()}.json")
    if not os.path.exists(filepath):
        print(f"Character '{name}' not found.")
        return None
    with open(filepath, "r") as f:
        return json.load(f)

def list_characters():
    ensure_characters_dir()
    files = [f.replace(".json", "") for f in os.listdir(CHARACTERS_DIR) if f.endswith(".json")]
    return files

def create_character():
    print("\n=== Create New Character ===")
    name        = input("Name: ")
    personality = input("Personality (e.g. witty, sarcastic, calm): ")
    role        = input("Role (e.g. study buddy, mentor, philosopher): ")
    backstory   = input("Backstory: ")

    character = {
        "name": name,
        "personality": personality,
        "role": role,
        "backstory": backstory
    }
    save_character(character)
    return character
