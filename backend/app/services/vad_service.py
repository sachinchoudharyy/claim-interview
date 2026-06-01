import numpy as np


def contains_speech(audio_bytes):

    if not audio_bytes:
        return False

    audio = np.frombuffer(audio_bytes, dtype=np.int16)

    if len(audio) == 0:
        return False

    energy = np.mean(np.abs(audio))

    # threshold tuned for microphone speech
    if energy < 500:
        return False

    return True