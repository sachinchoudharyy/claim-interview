import librosa
import noisereduce as nr

def denoise_audio(audio_path):
    y, sr = librosa.load(audio_path, sr=16000)
    y_reduced = nr.reduce_noise(y=y, sr=sr)
    return y_reduced, sr