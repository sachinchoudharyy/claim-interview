import cv2
import numpy as np
import mediapipe as mp
import sys, os

sys.path.append(os.path.dirname(__file__))

from depth_analyzer_v2 import detect_depth_parallax
from rppg_analyzer import analyze_rppg
from antispoof import AntiSpoofModel   # ✅ NEW

# Landmarks
LEFT_EYE_LANDMARKS = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_LANDMARKS = [33, 160, 158, 133, 153, 144]
NOSE_TIP = 1

CLOSED_EAR_THRESHOLD = 0.28
BLINK_CONSEC_FRAMES = 2

mp_face_mesh = mp.solutions.face_mesh


# ---------------- UTIL ----------------
def normalize(val, min_val, max_val):
    return max(0.0, min(1.0, (val - min_val) / (max_val - min_val + 1e-6)))


# ---------------- BASIC FEATURES ----------------
def calculate_ear(eye_landmarks, landmarks, width, height):
    def to_pixel(p): return np.array([p.x * width, p.y * height])
    pts = [to_pixel(landmarks[i]) for i in eye_landmarks]
    A = np.linalg.norm(pts[1] - pts[5])
    B = np.linalg.norm(pts[2] - pts[4])
    C = np.linalg.norm(pts[0] - pts[3])
    return (A + B) / (2.0 * C)


def estimate_head_movement(seq):
    if len(seq) < 2:
        return 0.0
    return np.mean([
        np.linalg.norm(np.array(seq[i][NOSE_TIP]) - np.array(seq[i-1][NOSE_TIP]))
        for i in range(1, len(seq))
    ])


def detect_texture(video_path):
    cap = cv2.VideoCapture(video_path)
    glare_vals, texture_vals = [], []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        glare_vals.append(np.sum(gray > 240) / gray.size)

        fft = np.fft.fft2(gray)
        mag = 20 * np.log(np.abs(np.fft.fftshift(fft)) + 1)
        texture_vals.append(np.mean(mag))

    cap.release()

    return {
        "fake": (np.mean(glare_vals) > 0.05 or np.mean(texture_vals) < 10)
    }


def detect_screen(video_path):
    cap = cv2.VideoCapture(video_path)
    lap_vals, bright_vals = [], []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        lap_vals.append(cv2.Laplacian(gray, cv2.CV_64F).var())
        bright_vals.append(np.mean(gray))

    cap.release()

    lap = np.mean(lap_vals) if lap_vals else 0
    flicker = np.std(bright_vals) if bright_vals else 0

    return normalize(lap, 50, 300) * 0.6 + (1 - normalize(flicker, 0, 20)) * 0.4


def detect_liveness_from_bytes(video_bytes):
    import tempfile
    import os

    # create temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(video_bytes)
        temp_path = tmp.name

    try:
        result = detect_liveness(temp_path)
        return result
    finally:
        try:
            os.remove(temp_path)
        except:
            pass


# ---------------- MAIN ----------------
def detect_liveness(video_path):

    cap = cv2.VideoCapture(video_path)

    # ✅ NEW MODEL INIT
    model = AntiSpoofModel("app/models/liveness_models/modelrgb.onnx")
    antispoof_scores = []

    frame_count = 0
    blink_count = 0
    closed = 0
    landmark_seq = []

    with mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1) as face_mesh:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # ✅ DEEP MODEL PREDICTION
            antispoof_scores.append(model.predict(frame))

            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = face_mesh.process(rgb)

            if res.multi_face_landmarks:
                lm = res.multi_face_landmarks[0].landmark

                ear = (
                    calculate_ear(LEFT_EYE_LANDMARKS, lm, w, h) +
                    calculate_ear(RIGHT_EYE_LANDMARKS, lm, w, h)
                ) / 2

                if ear < CLOSED_EAR_THRESHOLD:
                    closed += 1
                else:
                    if closed >= BLINK_CONSEC_FRAMES:
                        blink_count += 1
                    closed = 0

                landmark_seq.append([(p.x, p.y, p.z) for p in lm])

            frame_count += 1

    cap.release()

    # -------- METRICS --------
    head_score = estimate_head_movement(landmark_seq)
    texture = detect_texture(video_path)
    depth = detect_depth_parallax(video_path)
    rppg = analyze_rppg(video_path)
    screen = detect_screen(video_path)

    # -------- BASE SYSTEM --------
    rppg_conf = rppg.get("rppg_confidence", 0)
    depth_conf = normalize(depth.get("temporal_relative_variance", 0), 0, 150)
    motion_conf = normalize(head_score, 0.001, 0.01)
    texture_conf = 0.8 if not texture["fake"] else 0.2
    screen_conf = screen

    base_conf = (
        0.15 * rppg_conf +
        0.25 * depth_conf +
        0.25 * motion_conf +
        0.15 * texture_conf +
        0.20 * screen_conf
    )

    # -------- DEEP MODEL --------
    antispoof_conf = np.mean(antispoof_scores) if antispoof_scores else 0

    # -------- FINAL FUSION --------
    final_conf = 0.6 * antispoof_conf + 0.4 * base_conf

    # -------- DECISION --------
    if final_conf >= 0.75:
        status = "Live (High Confidence)"
        live = True
    elif final_conf >= 0.55:
        status = "Likely Live"
        live = True
    elif final_conf >= 0.35:
        status = "Uncertain"
        live = False
    else:
        status = "Spoof"
        live = False

    return {
        "liveness": live,
        "confidence": round(float(final_conf), 3),
        "status": status,
        "blinks": blink_count,
        "head_motion": round(float(head_score), 5),
        "final_reason": f"{status} | AI={round(float(antispoof_conf),2)}, base={round(float(base_conf),2)}"
    }