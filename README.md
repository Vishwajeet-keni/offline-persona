# OfflinePersona

A private, offline, character-driven AI assistant with voice input and output.
Runs entirely on your machine — no internet required, no data ever leaves your device.

---

## The Problem

Most AI assistants send your conversations to remote servers. OfflinePersona solves this
by running everything locally — the language model, speech recognition, and text-to-speech
all run on your machine with zero cloud dependency.

---

## Features

- **100% offline** — no API keys, no internet, no data sent anywhere
- **Custom characters** — define name, personality, role, and backstory
- **Stays in character** — consistent personality throughout the conversation
- **Voice input** — hold the mic button and speak, text is auto-transcribed
- **Voice output** — responses are spoken aloud with markdown cleaned automatically
- **Persistent history** — save and resume conversations per character
- **Dark GUI** — clean PyQt6 interface

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- `gemma2:2b` model pulled via Ollama
- 4GB+ RAM recommended

---

## Setup

**1. Clone the repository**
```bash
git clone git@github.com:Vishwajeet-keni/offline-persona.git
cd offline-persona
```

**2. Create and activate virtual environment**
```bash
python -m venv venv

# bash/zsh
source venv/bin/activate

# fish shell
source venv/bin/activate.fish
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Pull the model**
```bash
ollama pull gemma2:2b
```

**5. Download Piper voice model**
```bash
mkdir -p voice/models
cd voice/models
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
cd ../..
```

**6. Run**
```bash
python main.py
```

---

## Usage

| Action | How |
|---|---|
| Send a message | Type in the input box, press Enter |
| New line in input | Shift + Enter |
| Voice input | Hold 🎤, speak, release — text auto-fills |
| Switch character | Click "Switch Character" button |
| Resume conversation | Select from history list on startup |
| Exit | Close the window — history saves automatically |

---

## Project Structure
```
offline-persona/
├── main.py                  # Entry point
├── core/
│   ├── character.py         # Character create/save/load
│   ├── chat.py              # Ollama communication
│   └── storage.py           # History save/load
├── ui/
│   ├── main_window.py       # Chat window (PyQt6)
│   ├── character_dialog.py  # Character selection dialog
│   └── style.qss            # Dark theme stylesheet
├── voice/
│   ├── stt.py               # Speech-to-text (faster-whisper)
│   ├── tts.py               # Text-to-speech (Piper)
│   └── models/              # Voice model files (not in git)
├── characters/              # Character JSON files
├── histories/               # Saved conversations (not in git)
└── requirements.txt
```

---

## Troubleshooting

**Ollama not running**
```bash
ollama serve
ollama list   # verify gemma2:2b is available
```

**No audio output**
```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

**Fish shell venv activation**
```bash
source venv/bin/activate.fish
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Language model | Ollama + gemma2:2b |
| GUI | PyQt6 |
| Speech-to-text | faster-whisper (tiny, CPU) |
| Text-to-speech | Piper (en_US-lessac-medium) |
| Audio | sounddevice + numpy |
| Storage | JSON (local files) |

---

## Future Scope

- Character memory across sessions
- Multiple TTS voices per character
- Streaming token-by-token responses
- Export conversations to PDF
- Multi-language support

---

*Built with privacy in mind. All processing is local. Nothing leaves your device.*