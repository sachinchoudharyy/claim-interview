
import cv2
import numpy as np
import mediapipe as mp
from scipy.signal import butter, filtfilt, welch
from scipy.stats import pearsonr

try:
    mp_face_mesh = mp.solutions.face_mesh
except AttributeError:
    from mediapipe.python.solutions import face_mesh as mp_face_mesh

# Facial landmarks for forehead and cheeks
FOREHEAD_POINTS = [10, 338, 297, 332, 284, 251]
LEFT_CHEEK_POINTS = [50, 101, 118, 228]
RIGHT_CHEEK_POINTS = [280, 330, 347, 448]

# Bandpass filter (0.7 - 4 Hz -> 40 - 240 BPM)
def bandpass_filter(signal, fs, low, high):
    nyquist = 0.5 * fs
    low_cut = low / nyquist
    high_cut = high / nyquist
    b, a = butter(1, [low_cut, high_cut], btype='band')
    return filtfilt(b, a, signal)

def extract_roi_mean(frame, landmarks, indices):
    """Extract mean R, G, B values from a facial ROI."""
    h, w = frame.shape[:2]
    points = [landmarks[i] for i in indices]
    x_coords = [int(p.x * w) for p in points]
    y_coords = [int(p.y * h) for p in points]
    x_min, x_max = max(0, min(x_coords)), min(w, max(x_coords))
    y_min, y_max = max(0, min(y_coords)), min(h, max(y_coords))
    roi = frame[y_min:y_max, x_min:x_max]
    if roi.size == 0:
        return None
    return np.mean(roi[:, :, 0]), np.mean(roi[:, :, 1]), np.mean(roi[:, :, 2])  # B, G, R

def analyze_rppg(video_path, sample_rate=30, min_frames=150, debug=False):
    """
    Analyze rPPG signals using multi-region, multi-window analysis with weighted scoring.
    """
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    forehead_rgb, left_rgb, right_rgb = [], [], []

    with mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True) as face_mesh:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark

                f_mean = extract_roi_mean(frame, landmarks, FOREHEAD_POINTS)
                l_mean = extract_roi_mean(frame, landmarks, LEFT_CHEEK_POINTS)
                r_mean = extract_roi_mean(frame, landmarks, RIGHT_CHEEK_POINTS)

                if f_mean and l_mean and r_mean:
                    forehead_rgb.append(f_mean)
                    left_rgb.append(l_mean)
                    right_rgb.append(r_mean)

            frame_count += 1

    cap.release()

    if len(forehead_rgb) < min_frames:
        return {
            "rppg_detected": False,
            "signal_strength": 0,
            "heartbeat_bpm": 0,
            "avg_corr": 0,
            "bpm_consistency": 999,
            "green_dominant": False,
            "debug": {"frames": frame_count, "status": "Insufficient frames"}
        }

    # Separate green channels
    forehead_g = np.array([c[1] for c in forehead_rgb])
    left_g = np.array([c[1] for c in left_rgb])
    right_g = np.array([c[1] for c in right_rgb])

    # Normalize
    forehead_g = (forehead_g - np.mean(forehead_g)) / np.std(forehead_g)
    left_g = (left_g - np.mean(left_g)) / np.std(left_g)
    right_g = (right_g - np.mean(right_g)) / np.std(right_g)

    # Apply bandpass filter
    f_filt = bandpass_filter(forehead_g, sample_rate, 0.7, 4)
    l_filt = bandpass_filter(left_g, sample_rate, 0.7, 4)
    r_filt = bandpass_filter(right_g, sample_rate, 0.7, 4)

    # PSD
    freqs, psd_f = welch(f_filt, fs=sample_rate)
    freqs, psd_l = welch(l_filt, fs=sample_rate)
    freqs, psd_r = welch(r_filt, fs=sample_rate)

    max_freq_f = freqs[np.argmax(psd_f)]
    max_freq_l = freqs[np.argmax(psd_l)]
    max_freq_r = freqs[np.argmax(psd_r)]

    bpm_f = max_freq_f * 60
    bpm_l = max_freq_l * 60
    bpm_r = max_freq_r * 60
    bpm_consistency = max(bpm_f, bpm_l, bpm_r) - min(bpm_f, bpm_l, bpm_r)

    # Green channel dominance check
    forehead_r = np.array([c[2] for c in forehead_rgb])
    forehead_b = np.array([c[0] for c in forehead_rgb])
    forehead_r = (forehead_r - np.mean(forehead_r)) / np.std(forehead_r)
    forehead_b = (forehead_b - np.mean(forehead_b)) / np.std(forehead_b)

    r_psd = np.max(welch(bandpass_filter(forehead_r, sample_rate, 0.7, 4), fs=sample_rate)[1])
    b_psd = np.max(welch(bandpass_filter(forehead_b, sample_rate, 0.7, 4), fs=sample_rate)[1])
    g_psd = np.max(psd_f)
    green_dominant = g_psd > r_psd * 1.1 and g_psd > b_psd * 1.1  # Slightly looser condition

    # Correlation across regions
    corr_fl, _ = pearsonr(f_filt, l_filt)
    corr_fr, _ = pearsonr(f_filt, r_filt)
    corr_lr, _ = pearsonr(l_filt, r_filt)
    avg_corr = (abs(corr_fl) + abs(corr_fr) + abs(corr_lr)) / 3.0

    # Signal strength
    signal_strength = (np.max(psd_f) + np.max(psd_l) + np.max(psd_r)) / 3.0

    # Weighted scoring
    score = 0
    if signal_strength > 0.07: score += 1
    if bpm_consistency < 30: score += 1
    if avg_corr > 0.25: score += 1
    if green_dominant: score += 1

    rppg_detected = score >= 2  # At least 2 conditions must pass

    debug_info = {
        "bpm_forehead": round(bpm_f, 2),
        "bpm_left_cheek": round(bpm_l, 2),
        "bpm_right_cheek": round(bpm_r, 2),
        "bpm_consistency": round(bpm_consistency, 2),
        "corr_forehead_left": round(corr_fl, 3),
        "corr_forehead_right": round(corr_fr, 3),
        "corr_left_right": round(corr_lr, 3),
        "avg_corr": round(avg_corr, 3),
        "green_dominant": green_dominant,
        "signal_strength": round(signal_strength, 5),
        "frames": frame_count,
        "score": score
    }

    if debug:
        print("DEBUG RPPG:", debug_info)

    return {
        "rppg_detected": bool(rppg_detected),
        "signal_strength": round(float(signal_strength), 5),
        "heartbeat_bpm": round(float((bpm_f + bpm_l + bpm_r) / 3.0), 2),
        "avg_corr": round(float(avg_corr), 3),
        "bpm_consistency": round(float(bpm_consistency), 2),
        "green_dominant": bool(green_dominant),
        "score": score,
        "debug": debug_info
    }
