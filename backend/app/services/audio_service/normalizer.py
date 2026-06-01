import librosa

def normalize_audio(y):
    return librosa.util.normalize(y)
