from character import create_character, load_character, list_characters
from chat import chat, build_history
from storage import save_history, select_history

def select_character():
    characters = list_characters()

    if not characters:
        print("No characters found. Let's create one!")
        return create_character()

    print("\nAvailable characters:")
    for i, name in enumerate(characters, 1):
        print(f"{i}. {name}")
    print(f"{len(characters) + 1}. Create new character")

    choice = input("\nSelect: ")

    try:
        choice = int(choice)
        if choice == len(characters) + 1:
            return create_character()
        else:
            return load_character(characters[choice - 1])
    except:
        print("Invalid choice.")
        return select_character()


def main():
    print("=== OfflinePersona ===")
    print("A private, offline, character-driven AI assistant\n")

    character = select_character()
    if not character:
        return

    print(f"\nNow talking to: {character['name']}")
    print(f"Role: {character['role']}")
    print("Type 'quit' to exit\n")
    print("-" * 40)

    # load previous history or start fresh
    history = select_history(character['name']) or []

    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            save_history(character['name'], history)
            print("Goodbye!")
            break

        history = build_history(character, user_input, history)
        reply, history = chat(character, history)
        print(f"\n{character['name']}: {reply}\n")


if __name__ == "__main__":
    main()
