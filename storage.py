import json
import os
from datetime import datetime

HISTORY_DIR = "histories"

def ensure_history_dir():
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

def save_history(character_name, history):
    ensure_history_dir()
    date = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{character_name.lower()}_{date}.json"
    filepath = os.path.join(HISTORY_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(history, f, indent=4)
    print(f"\nConversation saved!")

def list_histories(character_name):
    ensure_history_dir()
    files = [
        f for f in os.listdir(HISTORY_DIR)
        if f.startswith(character_name.lower()) and f.endswith(".json")
    ]
    return sorted(files, reverse=True)  # most recent first

def load_history(filename):
    filepath = os.path.join(HISTORY_DIR, filename)
    with open(filepath, "r") as f:
        return json.load(f)

def select_history(character_name):
    histories = list_histories(character_name)

    if not histories:
        return None

    print(f"\nPrevious conversations with {character_name}:")
    for i, name in enumerate(histories, 1):
        print(f"{i}. {name}")
    print(f"{len(histories) + 1}. Start fresh")

    choice = input("\nSelect: ")

    try:
        choice = int(choice)
        if choice == len(histories) + 1:
            return None
        else:
            return load_history(histories[choice - 1])
    except:
        print("Invalid choice, starting fresh.")
        return None
