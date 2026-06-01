AUDIO_SAMPLE_RATE = 48000

# audio chunk size before sending to STT (seconds)
AUDIO_CHUNK_SECONDS = 2

# minimum text length to accept transcript
MIN_TRANSCRIPT_LENGTH = 3

# phrases commonly hallucinated by whisper
TRANSCRIPT_BLACKLIST = [
    "thank you for watching",
    "thanks for watching",
    "subscribe",
    "music",
    "applause",
    "background noise",
    "bye bye",
    "good night",
]

# reverse geocoding endpoint
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"