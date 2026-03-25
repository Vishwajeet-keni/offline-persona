# Project Report — OfflinePersona

## 1. Problem Statement

Most AI assistants available today — ChatGPT, Gemini, Microsoft Copilot — operate by sending
user conversations to remote servers. This means every message, question, and personal thought
shared with the AI is transmitted over the internet and stored on infrastructure owned by large
corporations. For users who deal with sensitive topics, personal matters, or confidential work,
this is a genuine privacy concern.

The problem this project addresses is simple: people want the benefits of an AI assistant
without sacrificing their privacy.

## 2. Why It Matters

Privacy is not just a technical concern — it is a human one. A student asking for help
understanding a difficult topic, a developer debugging sensitive code, or someone simply
wanting a judgment-free space to think out loud — all of these people deserve a tool that
respects their data.

Beyond privacy, there is also the question of availability. Cloud-based AI assistants require
a stable internet connection. A fully local assistant works anywhere, anytime, with no
dependency on external services.

## 3. Solution

OfflinePersona is a terminal-based AI assistant that runs entirely on the user's machine.
It uses Ollama to serve a local language model (gemma2:2b) and the Python ollama library
to interact with it. No data ever leaves the device.

What makes OfflinePersona different from a generic local chatbot is its character system.
Users can define custom AI personas — giving them a name, personality, role, and backstory.
The assistant then stays in character throughout the conversation, making interactions feel
more personal and purposeful than talking to a generic assistant.

## 4. Technical Approach

The project is built in Python and organized into four modules:

**main.py** serves as the entry point. It presents a menu that allows the user to select an
existing character or create a new one, then starts the chat loop.

**character.py** handles the creation, saving, and loading of character definitions. Each
character is stored as a JSON file in the characters/ directory. The character's name,
personality, role, and backstory are used to construct a system prompt that is injected
at the beginning of every conversation.

**chat.py** manages communication with the Ollama API. It maintains a conversation history
list that is passed with every request, giving the model full context of the conversation.
This is how the assistant appears to remember previous messages — the model itself is
stateless, but the history provides the context.

**storage.py** handles saving and loading conversation history. When a user quits, the full
conversation is saved as a timestamped JSON file in the histories/ directory. On the next
session, the user can choose to resume any previous conversation with a character.

## 5. Key Decisions

**Choosing Ollama over direct model loading** — Ollama provides a clean local API that
abstracts away model management. This made it easy to swap models and kept the Python
code simple.

**Choosing gemma2:2b** — A 2 billion parameter model is small enough to run comfortably
on CPU-only hardware while still producing coherent, useful responses.

**Storing history as plain JSON** — Simple, human-readable, and easy to load back. No
database required, which fits the lightweight nature of the project.

**Keeping histories/ out of Git** — Since the project is privacy-focused, it would be
contradictory to commit personal conversation logs to a public repository. The .gitignore
explicitly excludes this folder.

**Character system via system prompts** — Rather than fine-tuning a model (which is
computationally expensive), personality is injected through a system prompt at the start
of each conversation. This is a lightweight but effective approach.

## 6. Challenges Faced

**Fish shell compatibility** — The standard Python venv activation script does not work
in fish shell. The fix was to use the venv/bin/activate.fish script instead, which fish
provides out of the box.

**Git push rejection** — The GitHub repository was initialized with a license file,
causing a conflict with the local initial commit. This was resolved with a force push
since the repository was brand new.

**Understanding stateless models** — Early in the project it was not immediately obvious
why conversation history needed to be managed manually. Understanding that the model
has no memory between requests, and that context must be passed explicitly, was a
key learning moment.

## 7. What I Learned

This project reinforced several concepts covered in the course:

- How large language models work in practice — stateless inference, context windows,
  and the role of conversation history
- How to structure a multi-file Python project with clear separation of concerns
- How to use virtual environments and manage dependencies properly
- How system prompts can be used to shape model behavior without any training
- The practical difference between cloud AI and locally hosted models

## 8. Future Scope

The terminal interface is functional but limited. The next planned version of this project
includes a PyQt6 graphical interface with a dark theme, making the assistant more accessible
to non-technical users. Voice input via faster-whisper (STT) and voice output via Piper (TTS)
are also planned, which would make OfflinePersona a fully hands-free, private voice assistant.

These features were scoped out of the current submission due to time constraints, but the
modular structure of the codebase was designed with these additions in mind.

## 9. Conclusion

OfflinePersona demonstrates that a useful, personalized AI assistant can be built and run
entirely on a personal machine with no cloud dependency. The project is small in scale but
purposeful in design — every decision, from model choice to file structure to Git hygiene,
was made with the core goal of privacy in mind.
