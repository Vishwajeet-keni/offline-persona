import io
import wave
import re
import numpy as np
import sounddevice as sd
from piper.voice import PiperVoice
from threading import Lock

MODEL_PATH = "voice/models/en_US-lessac-medium.onnx"

print("Loading Piper voice model...")
voice = PiperVoice.load(MODEL_PATH)
print("Piper voice model loaded.")

# Piper's native output rate
PIPER_RATE = 22050
OUTPUT_RATE = None
_tts_lock = Lock()
_synthesis_cache = {}

def find_best_sample_rate():
    quick_rates = [44100, 48000]
    for rate in quick_rates:
        try:
            test_audio = np.zeros(100, dtype=np.float32)
            sd.play(test_audio, samplerate=rate, blocking=False)
            sd.wait()
            sd.stop()
            return rate
        except:
            continue
    try:
        device_id = sd.default.device[1]
        device_info = sd.query_devices(device_id, 'output')
        return int(device_info['default_samplerate'])
    except:
        return 44100

OUTPUT_RATE = find_best_sample_rate()
print(f"Using {OUTPUT_RATE} Hz")

def remove_emojis(text):
    """Remove all emojis and special Unicode characters"""
    # Comprehensive emoji removal
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental
        "\U0001FA70-\U0001FAFF"  # more emojis
        "\U00002500-\U00002BEF"  # various symbols
        "\U0000FE0F"              # variation selector
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def clean_text_for_speech(text):
    """
    Clean text for speech - removes ALL markdown, emojis, special chars
    """
    if not text:
        return ""
    
    # Remove emojis first
    text = remove_emojis(text)
    
    # Remove markdown
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'\_\_([^_]+)\_\_', r'\1', text)
    text = re.sub(r'\_([^_]+)\_', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'#{1,6}\s+', '', text)
    text = re.sub(r'[\\/*_`~\[\]\(\)]', '', text)
    text = re.sub(r'\|', ' ', text)
    text = re.sub(r'\-{3,}', ' ', text)
    
    # Remove any remaining non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    # Clean spaces
    text = re.sub(r'\n\s*\n', '. ', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Add natural pauses
    text = re.sub(r'\.\.\.', '... ', text)
    text = re.sub(r'!', '! ', text)
    text = re.sub(r'\?', '? ', text)
    text = re.sub(r',', ', ', text)
    
    # Common abbreviations
    abbreviations = {
        r'\bUN\b': 'United Nations',
        r'\bUS\b': 'U S',
        r'\bUSA\b': 'U S A',
        r'\bUK\b': 'United Kingdom',
        r'\bAI\b': 'A I',
        r'\bCEO\b': 'C E O',
        r'\bCFO\b': 'C F O',
        r'\bDr\.?\b': 'Doctor',
        r'\bMr\.?\b': 'Mister',
    }
    for pattern, replacement in abbreviations.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Final cleanup
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Ensure sentences end properly
    if text and text[-1] not in '.!?':
        text += '.'
    
    return text

def synthesize_audio(text):
    """Synthesize audio with caching"""
    # Clean text
    cleaned = clean_text_for_speech(text)
    
    # Skip empty
    if not cleaned.strip():
        return np.array([], dtype=np.float32)
    
    # Check cache
    if cleaned in _synthesis_cache:
        return _synthesis_cache[cleaned]
    
    # Synthesize
    wav_io = io.BytesIO()
    wav_file = wave.open(wav_io, "wb")
    voice.synthesize_wav(cleaned, wav_file)
    wav_file.close()
    
    wav_io.seek(0)
    with wave.open(wav_io, "rb") as f:
        frames = f.readframes(f.getnframes())
        original_rate = f.getframerate()
    
    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    
    # Resample if needed
    if original_rate != OUTPUT_RATE:
        ratio = OUTPUT_RATE / original_rate
        target_length = int(len(audio) * ratio)
        indices = np.linspace(0, len(audio) - 1, target_length)
        audio = np.interp(indices, np.arange(len(audio)), audio).astype(np.float32)
    
    # Cache
    _synthesis_cache[cleaned] = audio
    
    return audio

def speak(text, async_play=False):
    """Speak text - caches repeated phrases"""
    if not text or not text.strip():
        return
    
    try:
        audio = synthesize_audio(text)
        if len(audio) == 0:
            return
        
        with _tts_lock:
            sd.play(audio, samplerate=OUTPUT_RATE, blocking=not async_play)
            if not async_play:
                sd.wait()
    except Exception as e:
        print(f"Error in speak: {e}")

def preload_phrases(phrases):
    """Pre-synthesize common phrases"""
    for phrase in phrases:
        synthesize_audio(phrase)
    print(f"Preloaded {len(phrases)} phrases")

def clear_cache():
    global _synthesis_cache
    _synthesis_cache.clear()
    print("TTS cache cleared")

def get_cache_stats():
    return {"cached_phrases": len(_synthesis_cache), "output_rate": OUTPUT_RATE}

if __name__ == "__main__":
    common_phrases = ["Hello.", "Yes.", "No.", "Thank you.", "I'm sorry.", "Please wait."]
    preload_phrases(common_phrases)
    print("TTS ready!")