import sounddevice as sd
import numpy as np
import queue
import threading
from faster_whisper import WhisperModel

# load model once when module is imported
# using tiny model for speed on CPU
print("Loading Whisper model...")
model = WhisperModel("tiny", device="cpu", compute_type="int8")
print("Whisper model loaded.")

SAMPLE_RATE = 16000
audio_queue = queue.Queue()
is_recording = False
audio_frames = []


def start_recording():
    global is_recording, audio_frames
    audio_frames = []
    is_recording = True

    def callback(indata, frames, time, status):
        if is_recording:
            audio_frames.append(indata.copy())

    global stream
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        callback=callback
    )
    stream.start()


def stop_recording():
    global is_recording
    is_recording = False
    stream.stop()
    stream.close()

    if not audio_frames:
        return ""

    audio_data = np.concatenate(audio_frames, axis=0).flatten()
    return transcribe(audio_data)


def transcribe(audio_data):
    segments, _ = model.transcribe(audio_data, language="en")
    text = " ".join(segment.text for segment in segments)
    return text.strip()
