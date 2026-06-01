import os
import soundfile as sf
import numpy as np

from app.services.audio_service.extractor import extract_audio
from app.services.audio_service.denoiser import denoise_audio
from app.services.audio_service.normalizer import normalize_audio
from app.services.audio_service.hesitation import analyze_hesitation
from app.services.audio_service.stress_pyaudio import analyze_stress

from app.services.audio_service.whisper_engine import WhisperASR


def run_audio_pipeline(video_path):

    os.makedirs("temp", exist_ok=True)
    output_audio = "temp/audio.wav"

    try:
        # 1. Extract audio
        extract_audio(video_path, output_audio)

        # 2. Clean audio
        y, sr = denoise_audio(output_audio)
        y = normalize_audio(y)
        sf.write(output_audio, y, sr)

        # 3. Transcription (optional but useful)
        asr = WhisperASR(model_size="base")
        transcript = asr.transcribe(output_audio)

        # 4. Stress
        stress_score = analyze_stress(output_audio)

        # 5. Hesitation
        hesitation_score = analyze_hesitation(output_audio, transcript)

        # 🔥 REAL SILENCE DETECTION
        energy = np.abs(y)
        silence_threshold = np.mean(energy) * 0.2
        silence_frames = energy < silence_threshold
        silence_ratio = np.sum(silence_frames) / len(energy)

        # 🔥 VOICE ENERGY STABILITY
        energy_std = np.std(energy)
        energy_mean = np.mean(energy) + 1e-6
        energy_stability = 1 - (energy_std / energy_mean)
        energy_stability = max(0, min(1, energy_stability))

        # 🔥 NEW FEATURES

        # Speech rate
        words = transcript.strip().split()
        duration = max(len(y) / sr, 1)
        speech_rate = len(words) / duration  # words/sec

        # Silence ratio
        silence_ratio = hesitation_score  # already derived

        # Energy consistency
        energy_variation = abs(stress_score - 0.5)

        # 🔥 FINAL TRUST SCORE (IMPROVED)
        trust_score = (
            0.30 * (1 - stress_score) +
            0.25 * (1 - hesitation_score) +
            0.20 * min(speech_rate / 3.0, 1.0) +
            0.15 * energy_stability +
            0.10 * (1 - silence_ratio)
        )

        trust_score = round(trust_score * 100, 2)

        return {
            "stress": round(stress_score, 3),
            "hesitation": round(hesitation_score, 3),
            "speech_rate": round(speech_rate, 2),
            "silence_ratio": round(silence_ratio, 3),
            "energy_stability": round(energy_stability, 3),
            "trust_score": trust_score,
            "transcript": transcript
        }

    except Exception as e:
        print("AUDIO PIPELINE ERROR:", e)
        return None