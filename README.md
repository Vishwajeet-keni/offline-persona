# OfflinePersona

A private, offline, character-driven AI assistant that runs entirely on your machine. No internet required. No data ever leaves your device.

## The Problem

Most AI assistants (ChatGPT, Gemini, Copilot) send your conversations to remote servers. This raises serious privacy concerns — sensitive questions, personal data, and confidential work all leave your device. OfflinePersona solves this by running a local AI model with zero cloud dependency.

## Features

- 100% offline — no API keys, no internet, no data sent anywhere
- Create custom characters with a name, personality, role, and backstory
- The AI stays in character throughout the entire conversation
- Save and load conversation history per character
- Resume any previous conversation from where you left off

## How It Works
```
You → main.py → chat.py → Ollama (local) → gemma2:2b (on your machine)
```

Your conversation history is stored locally in the `histories/` folder and never leaves your device.

## Requirements

- Python 3.x
- [Ollama](https://ollama.com) installed and running
- gemma2:2b model pulled via Ollama

## Setup

**1. Clone the repository**
```bash
git clone git@github.com:Vishwajeet-keni/offline-persona.git
cd offline-persona
```

**2. Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # bash/zsh
source venv/bin/activate.fish   # fish shell
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Install Ollama and pull the model**
```bash
# Install Ollama from https://ollama.com
ollama pull gemma2:2b
```

**5. Run the app**
```bash
python main.py
```

## Usage

When you run the app you will see a menu to either select an existing character or create a new one. Creating a character looks like this:
```
=== Create New Character ===
Name: Alex
Personality: friendly, witty, speaks casually
Role: study buddy
Backstory: Alex is a 20 year old CS student who loves explaining things simply
```

Once a character is selected, you can start chatting. Type `quit` to end the session — your conversation will be saved automatically.

## Project Structure
```
offline-persona/
├── main.py          # Entry point and menu system
├── chat.py          # Ollama conversation logic
├── character.py     # Create, save, and load characters
├── storage.py       # Save and load chat history
├── characters/      # Character definitions (JSON)
├── histories/       # Saved conversations (JSON, local only)
└── requirements.txt
```

## Future Scope

- Voice input and output using local STT/TTS (Whisper + Piper)
- Web UI instead of terminal
- Character memory that persists facts across sessions
