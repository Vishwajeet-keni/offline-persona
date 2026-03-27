import ollama

def chat(character, history):
    response = ollama.chat(
        model="gemma2:2b",
        messages=history
    )
    reply = response["message"]["content"]
    history.append({"role": "assistant", "content": reply})
    return reply, history


def build_history(character, user_input, history):
    if len(history) == 0:
        system_prompt = f"""
        You are {character['name']}.
        Personality: {character['personality']}
        Role: {character['role']}
        Backstory: {character['backstory']}
        Stay in character at all times.
        """
        history.append({"role": "system", "content": system_prompt})

    history.append({"role": "user", "content": user_input})
    return history
