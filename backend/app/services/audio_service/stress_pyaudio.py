from pyAudioAnalysis import ShortTermFeatures
import numpy as np
import librosa

def analyze_stress(audio_path):
    y, sr = librosa.load(audio_path, sr=16000)

    # Extract short-term features
    features, _ = ShortTermFeatures.feature_extraction(
        y, sr, 0.05 * sr, 0.025 * sr
    )

    # Select stress-relevant features
    zcr = np.mean(features[0])
    energy = np.mean(features[1])
    spectral_centroid = np.mean(features[3])
    spectral_spread = np.mean(features[4])
    mfcc_std = np.mean(np.std(features[8:21], axis=1))

    # Normalize features
    zcr_n = min(zcr / 0.15, 1.0)
    energy_n = min(energy / 0.3, 1.0)
    centroid_n = min(spectral_centroid / 4000, 1.0)
    spread_n = min(spectral_spread / 3000, 1.0)
    mfcc_n = min(mfcc_std / 100, 1.0)

    # Weighted fusion
    stress_score = (
        0.25 * zcr_n +
        0.25 * energy_n +
        0.20 * centroid_n +
        0.15 * spread_n +
        0.15 * mfcc_n
    )

    stress_score = min(max(stress_score, 0), 1)
    return round(float(stress_score), 3)
