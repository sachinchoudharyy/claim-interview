import librosa
import numpy as np
import re


def analyze_hesitation(audio_path, transcript):
    y, sr = librosa.load(audio_path, sr=16000)

    # Detect silent region
    intervals = librosa.effects.split(y, top_db=25)
    total_audio_time = librosa.get_duration(y=y, sr=sr)

    voiced_time = sum((end - start) for start, end in intervals) / sr
    silence_time = max(0, total_audio_time - voiced_time)

    pause_ratio = silence_time / total_audio_time

    # Speech rate calculation
    words = transcript.strip().split()
    speech_rate = len(words) / total_audio_time  # words per second

    # Filler word detection
    filler_words = re.findall(r"\b(uh+|um+|aa+|hmm+|erm+)\b", transcript.lower())
    filler_ratio = len(filler_words) / max(len(words), 1)

    # Normalize features
    pause_norm = min(pause_ratio / 0.4, 1.0)
    rate_norm = 1 - min(speech_rate / 3.0, 1.0)
    filler_norm = min(filler_ratio / 0.1, 1.0)

    hesitation_score = (
        0.40 * pause_norm +
        0.35 * rate_norm +
        0.25 * filler_norm
    )

    return round(float(hesitation_score), 3)
