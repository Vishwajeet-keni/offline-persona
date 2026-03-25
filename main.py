import ollama

def chat():
    history = []
    print("AI Assistant ready. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break

        history.append({"role": "user", "content": user_input})

        response = ollama.chat(model="gemma2:2b", messages=history)
        reply = response["message"]["content"]

        history.append({"role": "assistant", "content": reply})
        print(f"AI: {reply}\n")

chat()
