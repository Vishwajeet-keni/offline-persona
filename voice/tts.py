import io
import wave
import re
import numpy as np
import sounddevice as sd
from piper.voice import PiperVoice

MODEL_PATH = "voice/models/en_US-lessac-medium.onnx"

print("Loading Piper voice model...")
voice = PiperVoice.load(MODEL_PATH)
print("Piper voice model loaded.")

# Piper's native output rate
PIPER_RATE = 22050
OUTPUT_RATE = None

def find_best_sample_rate():
    """Find best sample rate with minimal testing"""
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

def clean_text_for_speech(text):
    """
    Convert markdown/plain text to natural speech-friendly format.
    Removes special characters and adds natural pauses.
    """
    if not text:
        return ""
    
    # Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** -> bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic* -> italic
    text = re.sub(r'\_\_([^_]+)\_\_', r'\1', text)  # __bold__ -> bold
    text = re.sub(r'\_([^_]+)\_', r'\1', text)      # _italic_ -> italic
    text = re.sub(r'`([^`]+)`', r'\1', text)        # `code` -> code
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [text](url) -> text
    text = re.sub(r'#{1,6}\s+', '', text)           # # Headers -> Headers
    
    # Remove special characters but keep sentence structure
    text = re.sub(r'[\\/*_`~\[\]\(\)]', '', text)   # Remove remaining markdown chars
    text = re.sub(r'\|', ' ', text)                 # Table separators -> space
    text = re.sub(r'\-{3,}', ' ', text)             # --- -> pause
    text = re.sub(r'_{3,}', ' ', text)              # ___ -> pause
    
    # Clean up multiple spaces and newlines
    text = re.sub(r'\n\s*\n', '. ', text)           # Double newline -> period + space
    text = re.sub(r'\n', ' ', text)                 # Single newline -> space
    text = re.sub(r'\s+', ' ', text)                # Multiple spaces -> single space
    
    # Add natural pauses for punctuation
    text = re.sub(r'\.\.\.', '... ', text)          # Ellipsis with pause
    text = re.sub(r'!', '! ', text)                 # Exclamation with pause
    text = re.sub(r'\?', '? ', text)                # Question with pause
    text = re.sub(r',', ', ', text)                 # Comma with pause
    text = re.sub(r';', '; ', text)                 # Semicolon with pause
    text = re.sub(r':', ': ', text)                 # Colon with pause
    
    # Convert common abbreviations to spoken form
    abbreviations = {
        r'\bUN\b': 'United Nations',
        r'\bUS\b': 'U S',
        r'\bUSA\b': 'U S A',
        r'\bUK\b': 'United Kingdom',
        r'\bUAE\b': 'U A E',
        r'\bAI\b': 'A I',
        r'\bCEO\b': 'C E O',
        r'\bCFO\b': 'C F O',
        r'\bCTO\b': 'C T O',
        r'\bGDP\b': 'G D P',
        r'\bNATO\b': 'N A T O',
        r'\bWHO\b': 'W H O',
        r'\bIMF\b': 'I M F',
        r'\bUNESCO\b': 'Yoo Ness Co',
        r'\bNASA\b': 'Na Sa',
        r'\bMIT\b': 'M I T',
        r'\bPhD\b': 'P H D',
        r'\bDr\.?\b': 'Doctor',
        r'\bMr\.?\b': 'Mister',
        r'\bMs\.?\b': 'Miss',
        r'\bMrs\.?\b': 'Missus',
        r'\bSt\.?\b': 'Saint',
        r'\bAve\.?\b': 'Avenue',
        r'\bRd\.?\b': 'Road',
        r'\bBlvd\.?\b': 'Boulevard',
    }
    
    for pattern, replacement in abbreviations.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Clean up extra spaces and strip
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Ensure sentences end with proper punctuation
    if text and text[-1] not in '.!?':
        text += '.'
    
    return text

def add_emotional_tone(text):
    """
    Add natural emotional cues to the text for better delivery.
    This modifies the text slightly to help TTS sound more natural.
    """
    # Add natural pauses for emphasis
    text = re.sub(r'\!+', '! ', text)
    text = re.sub(r'\?+', '? ', text)
    
    # Convert emojis to words
    emoji_map = {
        '🌎': 'planet Earth',
        '🌍': 'planet Earth',
        '🌏': 'planet Earth',
        '😊': 'smiley face',
        '😢': 'sad',
        '😂': 'laughing',
        '🤔': 'thinking',
        '👀': 'look',
        '💪': 'strong',
        '🧠': 'brain',
        '✨': 'sparkle',
    }
    
    for emoji, word in emoji_map.items():
        text = text.replace(emoji, f' {word} ')
    
    # Add slight pauses around parenthetical thoughts
    text = re.sub(r'\(([^)]+)\)', r', \1, ', text)
    
    # Add natural breaks for lists (bullet points become pauses)
    text = re.sub(r'[\*\-•]\s+', '... ', text)
    
    return text

def optimize_audio(audio, original_rate, target_rate):
    """Optimized audio resampling"""
    if original_rate == target_rate:
        return audio
    
    ratio = target_rate / original_rate
    target_length = int(len(audio) * ratio)
    indices = np.linspace(0, len(audio) - 1, target_length)
    return np.interp(indices, np.arange(len(audio)), audio).astype(np.float32)

def speak(text):
    """
    Speak text naturally - cleans markdown and adds natural speech patterns
    """
    if not text or not text.strip():
        return
    
    try:
        # Clean and prepare text for natural speech
        cleaned = clean_text_for_speech(text)
        cleaned = add_emotional_tone(cleaned)
        
        # Optional: Print what's actually being spoken (for debugging)
        # print(f"[TTS Speaking]: {cleaned}")
        
        # Synthesize
        wav_io = io.BytesIO()
        wav_file = wave.open(wav_io, "wb")
        voice.synthesize_wav(cleaned, wav_file)
        wav_file.close()
        
        # Read audio
        wav_io.seek(0)
        with wave.open(wav_io, "rb") as f:
            frames = f.readframes(f.getnframes())
            original_rate = f.getframerate()
        
        # Convert to float32
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Resample if needed
        if original_rate != OUTPUT_RATE:
            audio = optimize_audio(audio, original_rate, OUTPUT_RATE)
        
        # Play
        sd.play(audio, samplerate=OUTPUT_RATE, blocking=True)
        
    except Exception as e:
        print(f"Error in speak: {e}")

def speak_with_emotion(text, emotion="neutral"):
    """
    Enhanced version with emotion hints.
    emotion can be: "neutral", "excited", "worried", "thoughtful", "emphatic"
    """
    if not text or not text.strip():
        return
    
    try:
        cleaned = clean_text_for_speech(text)
        
        # Add emotional modifiers based on context
        if emotion == "excited":
            # Add exclamation emphasis
            cleaned = cleaned.replace('.', '!')
            if not cleaned.endswith('!'):
                cleaned += '!'
        elif emotion == "worried":
            # Add thoughtful pauses
            cleaned = cleaned.replace('.', '... ')
        elif emotion == "thoughtful":
            # Add contemplative phrasing
            cleaned = f"Hmm... {cleaned}"
        elif emotion == "emphatic":
            # Add emphasis words
            cleaned = f"I must say, {cleaned}"
        
        cleaned = add_emotional_tone(cleaned)
        
        wav_io = io.BytesIO()
        wav_file = wave.open(wav_io, "wb")
        voice.synthesize_wav(cleaned, wav_file)
        wav_file.close()
        
        wav_io.seek(0)
        with wave.open(wav_io, "rb") as f:
            frames = f.readframes(f.getnframes())
            original_rate = f.getframerate()
        
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        
        if original_rate != OUTPUT_RATE:
            audio = optimize_audio(audio, original_rate, OUTPUT_RATE)
        
        sd.play(audio, samplerate=OUTPUT_RATE, blocking=True)
        
    except Exception as e:
        print(f"Error in speak_with_emotion: {e}")

# Test function
def test_tts():
    """Test the TTS with natural speech"""
    test_text = """
    Hey there! 👋 I'm your **offline assistant**. 
    I can talk naturally now, without reading *asterisks* or weird symbols.
    
    Let me ask you something... How can I help you today?
    """
    print("Testing TTS with natural speech...")
    speak(test_text)
    print("Done!")

if __name__ == "__main__":
    test_tts()
