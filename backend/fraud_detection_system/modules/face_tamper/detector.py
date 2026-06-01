import os

import cv2
import mediapipe as mp
import numpy as np

from fraud_detection_system.core.outputs import save_output

from fraud_detection_system.config import get_verdict

# =====================================================
# MEDIAPIPE
# =====================================================

mp_face_detection = mp.solutions.face_detection

face_detector = mp_face_detection.FaceDetection(

    model_selection=1,

    min_detection_confidence=0.5
)

# =====================================================
# DETECT FACES
# =====================================================

def detect_faces(image):

    rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    results = face_detector.process(
        rgb
    )

    faces = []

    if results.detections:

        h, w, _ = image.shape

        for detection in results.detections:

            bbox = detection.location_data.relative_bounding_box

            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)

            bw = int(bbox.width * w)
            bh = int(bbox.height * h)

            faces.append(
                (x, y, bw, bh)
            )

    return faces

# =====================================================
# MAIN PIPELINE
# =====================================================

def run_face_tamper_detection(
    image_path
):

    image = cv2.imread(image_path)

    filename = os.path.basename(
        image_path
    )

    faces = detect_faces(image)

    output = image.copy()

    total_score = 0

    face_regions = []

    for (x, y, w, h) in faces:

        face_crop = image[
            y:y+h,
            x:x+w
        ]

        # =====================================================
        # LOCAL ANALYSIS
        # =====================================================

        blur = cv2.GaussianBlur(

            face_crop,

            (5, 5),

            0
        )

        diff = cv2.absdiff(
            face_crop,
            blur
        )

        gray = cv2.cvtColor(
            diff,
            cv2.COLOR_BGR2GRAY
        )

        intensity = np.mean(gray)

        score = min(
            int(intensity * 2),
            100
        )

        total_score += score

        face_regions.append({

            "x": x,

            "y": y,

            "w": w,

            "h": h,

            "score": score
        })

        # =====================================================
        # DRAW
        # =====================================================

        color = (0, 255, 0)

        if score > 40:

            color = (0, 0, 255)

        cv2.rectangle(

            output,

            (x, y),

            (x+w, y+h),

            color,

            3
        )

    # =====================================================
    # FINAL SCORE
    # =====================================================

    if len(faces) > 0:

        final_score = int(
            total_score / len(faces)
        )

    else:

        final_score = 0

    # =====================================================
    # SAVE
    # =====================================================

    output_path = save_output(

        output,

        "overlay",

        f"face_tamper_{filename}"
    )

    return {

        "module": "face_tamper",

        "score": final_score,

        "verdict": get_verdict(
            final_score
        ),

        "faces_detected": len(
            faces
        ),

        "regions": face_regions,

        "images": {

            "visualization": output_path
        }
    }