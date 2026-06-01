
import cv2
import numpy as np
from midas_model import midas_model
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh


NOSE_TIP = 1
LEFT_CHEEK = 234
RIGHT_CHEEK = 454


def relative_depth(depth_map, landmarks, w, h):
    """Get relative depth between nose and cheeks."""
    def to_pixel(idx):
        lm = landmarks[idx]
        h_d, w_d = depth_map.shape  # use depth map size (256x256)
        return int(lm.x * w_d), int(lm.y * h_d)

    nose_px = to_pixel(NOSE_TIP)
    left_px = to_pixel(LEFT_CHEEK)
    right_px = to_pixel(RIGHT_CHEEK)

    nose_depth = depth_map[nose_px[1], nose_px[0]]
    left_depth = depth_map[left_px[1], left_px[0]]
    right_depth = depth_map[right_px[1], right_px[0]]

    return abs(nose_depth - left_depth) + abs(nose_depth - right_depth)


def detect_depth_parallax(video_path, num_frames=5, depth_threshold=0.3, temporal_threshold=0.02):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_indices = np.linspace(0, max(total_frames - 1, 0), num_frames).astype(int)

    frame_depth_variances = []
    relative_depths = []

    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue

            h, w = frame.shape[:2]
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame_rgb)
            if not results.multi_face_landmarks:
                continue

            landmarks = results.multi_face_landmarks[0].landmark
            depth_map = midas_model.estimate_depth(frame_rgb)
            frame_depth_variances.append(np.std(depth_map))

            rel_depth = relative_depth(depth_map, landmarks, w, h)
            relative_depths.append(rel_depth)

    cap.release()

    avg_depth_var = np.mean(frame_depth_variances) if frame_depth_variances else 0.0
    avg_rel_depth = np.mean(relative_depths) if relative_depths else 0.0
    temporal_rel_var = np.std(relative_depths) if len(relative_depths) > 1 else 0.0

    likely_flat = (avg_depth_var < depth_threshold or temporal_rel_var < temporal_threshold)

    # ---- NEW: temporal depth consistency ----
    depth_temporal_std = np.std(relative_depths) if relative_depths else 0.0

    # ---- BETTER DEPTH SCALING ----
    if depth_temporal_std < 5:
        depth_confidence = 0.2
    elif depth_temporal_std < 20:
        depth_confidence = 0.5
    else:
        depth_confidence = min(1.0, depth_temporal_std / 100)

    return {
        "avg_depth_variance": round(float(avg_depth_var), 5),
        "avg_relative_depth": round(float(avg_rel_depth), 5),
        "temporal_relative_variance": round(float(temporal_rel_var), 5),
        "depth_confidence": round(float(depth_confidence), 3),
        "likely_flat": likely_flat
    }

def detect_temporal_face_parallax(video_path, num_frames=12):
    """
    Detect replay by checking normalized facial depth deformation.
    Removes camera motion influence.
    """

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_indices = np.linspace(0, max(total_frames - 1, 0), num_frames).astype(int)

    ratios = []

    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue

            h, w = frame.shape[:2]
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame_rgb)

            if not results.multi_face_landmarks:
                continue

            landmarks = results.multi_face_landmarks[0].landmark
            depth_map = midas_model.estimate_depth(frame_rgb)

            def px(i):
                lm = landmarks[i]
                h_d, w_d = depth_map.shape  # use resized depth map size
                return int(lm.x * w_d), int(lm.y * h_d)

            # landmarks
            nose = depth_map[px(1)[1], px(1)[0]]
            left = depth_map[px(234)[1], px(234)[0]]
            right = depth_map[px(454)[1], px(454)[0]]

            cheek = (left + right) / 2.0

            # normalize by face width (removes camera motion)
            lx, ly = px(234)
            rx, ry = px(454)
            face_width = np.linalg.norm([lx-rx, ly-ry]) + 1e-6

            ratio = (nose - cheek) / face_width
            ratios.append(ratio)

    cap.release()

    if len(ratios) < 5:
        return {"parallax_score": 0.0, "likely_replay": True}

    ratios = np.array(ratios)

    temporal_change = np.std(ratios)

    return {
        "parallax_score": float(temporal_change),
        "likely_replay": temporal_change < 0.002
    }
