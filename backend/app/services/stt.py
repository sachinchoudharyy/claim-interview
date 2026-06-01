import io
import wave
import numpy as np
from groq import Groq
from app.core.config import GROQ_API_KEY
from app.core.constants import AUDIO_SAMPLE_RATE

client = Groq(api_key=GROQ_API_KEY)


def normalize_audio(audio_bytes):

    audio = np.frombuffer(audio_bytes, dtype=np.int16)

    if len(audio) == 0:
        return audio_bytes

    max_val = np.max(np.abs(audio))

    if max_val == 0:
        return audio_bytes

    normalized = (audio / max_val * 32767).astype(np.int16)

    return normalized.tobytes()


def pcm_to_wav_bytes(audio_bytes):

    audio_bytes = normalize_audio(audio_bytes)

    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wf:

        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(AUDIO_SAMPLE_RATE)

        wf.writeframes(audio_bytes)

    buffer.seek(0)

    return buffer.read()


def transcribe(audio_bytes, language="en"):

    if not audio_bytes:
        return ""

    wav_bytes = pcm_to_wav_bytes(audio_bytes)

    try:

        result = client.audio.transcriptions.create(
            file=("audio.wav", wav_bytes, "audio/wav"),
            model="whisper-large-v3",
            language=language
        )

        return result.text.strip()

    except Exception as e:

        print("STT error:", e)

        return ""


        