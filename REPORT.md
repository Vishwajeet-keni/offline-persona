# Project Report — OfflinePersona

## 1. Problem Statement

Most AI assistants available today — ChatGPT, Gemini, Microsoft Copilot — operate by
sending user conversations to remote servers. This means every message, question, and
personal thought shared with the AI is transmitted over the internet and stored on
infrastructure owned by large corporations. For users who deal with sensitive topics,
personal matters, or confidential work, this is a genuine privacy concern.

The problem this project addresses is simple: people want the benefits of a modern,
feature-rich AI assistant without sacrificing their privacy.

## 2. Why It Matters

Privacy is not just a technical concern — it is a human one. A student asking for help
understanding a difficult topic, a developer debugging sensitive code, or someone simply
wanting a judgment-free space to think out loud — all of these people deserve a tool
that respects their data.

Beyond privacy, there is also the question of availability. Cloud-based AI assistants
require a stable internet connection. A fully local assistant works anywhere, anytime,
with no dependency on external services.

## 3. Solution

OfflinePersona is a fully local, privacy-first AI assistant with a dark-themed graphical
interface, voice input, and voice output — all running entirely on the user's machine.
It uses Ollama to serve a local language model (gemma2:2b) and the Python ollama library
to interact with it. No data ever leaves the device.

What makes OfflinePersona different from a generic local chatbot is its character system.
Users can define custom AI personas — giving them a name, personality, role, and backstory.
The assistant stays in character throughout the conversation, making interactions feel
personal and purposeful rather than like talking to a generic search engine.

## 4. Technical Approach

The project is structured into four layers, each handled by a dedicated module:

**core/character.py** handles the creation, saving, and loading of character definitions.
Each character is stored as a JSON file in the characters/ directory. The character's
name, personality, role, and backstory are used to construct a system prompt that is
injected at the beginning of every conversation.

**core/chat.py** manages communication with the Ollama API. It maintains a conversation
history list that is passed with every request, giving the model full context of the
conversation. This is how the assistant appears to remember previous messages — the model
itself is stateless, but the history provides the context.

**core/storage.py** handles saving and loading conversation history. When a user closes
the app, the full conversation is saved as a timestamped JSON file in the histories/
directory. On the next session, the user can choose to resume any previous conversation.

**ui/main_window.py** is the PyQt6 chat window. It uses QThread workers to handle Ollama
requests and TTS synthesis without blocking the UI. The mic button uses pressed/released
signals to start and stop audio recording.

**voice/stt.py** handles speech-to-text using faster-whisper (tiny model, int8 quantized).
When the user holds the mic button, audio is recorded via sounddevice. On release, the
recording is transcribed and the result is auto-filled into the input box.

**voice/tts.py** handles text-to-speech using Piper. Before synthesis, the response text
is cleaned — markdown symbols, emojis, and formatting characters are stripped so the voice
output sounds natural. The audio is resampled to match the device's supported sample rate,
which is auto-detected at startup.

## 5. Key Decisions

**Choosing Ollama over direct model loading** — Ollama provides a clean local API that
abstracts away model management. This made it easy to swap models and kept the Python
code simple and decoupled from the model itself.

**Choosing gemma2:2b** — A 2 billion parameter model is small enough to run comfortably
on CPU-only hardware while still producing coherent, useful responses. This makes the
project accessible to users without a dedicated GPU.

**PyQt6 for the UI** — PyQt6 provides a native-looking, responsive interface. Using
QThread for all heavy operations (LLM inference, TTS synthesis, STT transcription) keeps
the UI non-blocking and responsive at all times.

**Storing history as plain JSON** — Simple, human-readable, and easy to load back. No
database required, which fits the lightweight and transparent nature of the project.

**Keeping histories/ out of Git** — Since the project is privacy-focused, it would be
contradictory to commit personal conversation logs to a public repository. The .gitignore
explicitly excludes this folder.

**Character system via system prompts** — Rather than fine-tuning a model (which is
computationally expensive), personality is injected through a system prompt at the start
of each conversation. This is a lightweight but surprisingly effective approach.

**Auto-detecting audio sample rate** — Different Linux audio setups (ALSA, PipeWire,
PulseAudio) support different sample rates. Rather than hardcoding a rate, the TTS module
queries the default output device at startup and resamples Piper's output to match.

**Stripping markdown before TTS** — LLMs naturally output markdown formatting. Without
cleaning, the TTS would read asterisks, hashes, and bullet symbols aloud. A regex-based
cleaning pipeline strips all formatting before synthesis.

## 6. Challenges Faced

**Fish shell venv activation** — The standard Python venv activation script does not work
in fish shell. The fix was to use venv/bin/activate.fish, which fish provides out of the box.

**Git push rejection** — The GitHub repository was initialized with a license file, causing
a conflict with the local initial commit. This was resolved with a force push since the
repository was brand new and the remote content was auto-generated.

**Understanding stateless models** — Early in the project it was not immediately obvious
why conversation history needed to be managed manually. Understanding that the model has
no memory between requests, and that context must be passed explicitly with every call,
was a key learning moment that shaped the entire architecture.

**ALSA sample rate incompatibility** — Piper synthesizes audio at 22050 Hz, but the ALSA
audio backend on the development machine rejected this rate. This required implementing
auto-detection of the device's native sample rate and resampling the audio using numpy
interpolation before playback.

**TTS reading markdown symbols** — The LLM responses contained heavy markdown formatting
which Piper would read literally (saying "asterisk asterisk" for bold text). This required
building a thorough text cleaning pipeline using regex to strip all formatting before
passing text to the TTS engine.

**Threading in PyQt6** — All heavy operations had to be moved off the main thread using
QThread to keep the UI responsive. Managing signals between worker threads and the main
UI thread required careful design to avoid race conditions.

## 7. What I Learned

This project reinforced and extended several concepts covered in the course:

- How large language models work in practice — stateless inference, context windows,
  system prompts, and conversation history management
- How to structure a multi-file Python project with clear separation of concerns across
  core logic, UI, and voice modules
- How to use virtual environments and manage dependencies properly on Linux
- How system prompts can be used to shape model behavior without any training or
  fine-tuning
- The practical difference between cloud AI and locally hosted models, and the
  real-world tradeoffs involved
- How to integrate multiple AI systems (LLM + STT + TTS) into a single coherent
  application
- How to handle threading in a GUI application to keep the interface responsive
- How audio pipelines work — sample rates, resampling, and device compatibility

## 8. Future Scope

- **Character memory** — persist facts the user mentions across sessions using a
  local vector store or simple key-value store
- **Multiple voices** — allow different TTS voices per character
- **Streaming responses** — display and speak text token by token as the model
  generates it rather than waiting for the full response
- **Export conversations** — save chat history as PDF or markdown
- **Custom wake word** — hands-free activation without pressing the mic button
- **Multi-language support** — STT and TTS in languages other than English

## 9. Conclusion

OfflinePersona demonstrates that a modern, feature-rich AI assistant — with a graphical
interface, voice input, voice output, and persistent memory — can be built and run entirely
on a personal machine with no cloud dependency. Every technical decision, from model choice
to file structure to audio pipeline design, was made with the core goal of privacy in mind.

The project evolved significantly during development. What started as a terminal chatbot
grew into a full PyQt6 application with integrated speech capabilities, each new feature
presenting its own engineering challenge. The result is a tool that is genuinely useful,
genuinely private, and genuinely runs offline.