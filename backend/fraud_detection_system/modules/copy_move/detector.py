import os

import cv2
import numpy as np

from fraud_detection_system.core.outputs import save_output

from fraud_detection_system.config import get_verdict

# =====================================================
# DETECT COPY MOVE
# =====================================================

def detect_copy_move(image_path):

    image = cv2.imread(image_path)

    if image is None:

        raise ValueError(
            "Unable to load image."
        )

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # =====================================================
    # ORB FEATURES
    # =====================================================

    orb = cv2.ORB_create(
        nfeatures=3000
    )

    keypoints, descriptors = orb.detectAndCompute(
        gray,
        None
    )

    if descriptors is None:

        return {

            "image": image,

            "keypoints": [],

            "matches": [],

            "score": 0
        }

    # =====================================================
    # MATCHING
    # =====================================================

    matcher = cv2.BFMatcher(

        cv2.NORM_HAMMING,

        crossCheck=True
    )

    matches = matcher.match(
        descriptors,
        descriptors
    )

    filtered_matches = []

    for match in matches:

        if match.distance < 25:

            pt1 = keypoints[
                match.queryIdx
            ].pt

            pt2 = keypoints[
                match.trainIdx
            ].pt

            spatial_distance = np.linalg.norm(

                np.array(pt1) -

                np.array(pt2)
            )

            if spatial_distance > 25:

                filtered_matches.append(
                    match
                )

    filtered_matches = sorted(

        filtered_matches,

        key=lambda x: x.distance
    )

    filtered_matches = filtered_matches[:100]

    score = min(
        int(len(filtered_matches) * 1.5),
        100
    )

    return {

        "image": image,

        "keypoints": keypoints,

        "matches": filtered_matches,

        "score": score
    }

# =====================================================
# DRAW MATCHES
# =====================================================

def draw_matches(
    image,
    keypoints,
    matches
):

    output = image.copy()

    for match in matches:

        pt1 = tuple(

            map(
                int,
                keypoints[match.queryIdx].pt
            )
        )

        pt2 = tuple(

            map(
                int,
                keypoints[match.trainIdx].pt
            )
        )

        cv2.circle(
            output,
            pt1,
            5,
            (0, 0, 255),
            -1
        )

        cv2.circle(
            output,
            pt2,
            5,
            (255, 0, 0),
            -1
        )

        cv2.line(
            output,
            pt1,
            pt2,
            (0, 255, 0),
            2
        )

    return output

# =====================================================
# MAIN PIPELINE
# =====================================================

def run_copy_move_detection(
    image_path
):

    filename = os.path.basename(
        image_path
    )

    result = detect_copy_move(
        image_path
    )

    image = result["image"]

    keypoints = result["keypoints"]

    matches = result["matches"]

    score = result["score"]

    visualization = draw_matches(

        image,

        keypoints,

        matches
    )

    output_path = save_output(

        visualization,

        "overlay",

        f"copy_move_{filename}"
    )

    return {

        "module": "copy_move",

        "score": score,

        "verdict": get_verdict(
            score
        ),

        "matches_detected": len(
            matches
        ),

        "images": {

            "visualization": output_path
        }
    }