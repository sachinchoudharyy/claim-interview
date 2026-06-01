import os
import uuid

import cv2
import numpy as np

from fraud_detection_system.core.outputs import save_output

from fraud_detection_system.config import (
    TEMP_DIR,
    get_verdict
)

# =====================================================
# PERFORM ELA
# =====================================================

def perform_ela(

    image_path,

    quality=75,

    scale=35
):

    img = cv2.imread(image_path)

    if img is None:

        raise ValueError(
            "Unable to load image for ELA."
        )

    temp_filename = f"{uuid.uuid4().hex}.jpg"

    temp_path = os.path.join(
        TEMP_DIR,
        temp_filename
    )

    cv2.imwrite(

        temp_path,

        img,

        [
            int(cv2.IMWRITE_JPEG_QUALITY),
            quality
        ]
    )

    compressed = cv2.imread(temp_path)

    diff = cv2.absdiff(
        img,
        compressed
    )

    ela = diff.astype(np.float32) * scale

    max_diff = ela.max()

    if max_diff > 0:

        ela = ela * (255.0 / max_diff)

    ela = np.clip(
        ela,
        0,
        255
    ).astype(np.uint8)

    ela_lab = cv2.cvtColor(
        ela,
        cv2.COLOR_BGR2LAB
    )

    l, a, b = cv2.split(ela_lab)

    clahe = cv2.createCLAHE(

        clipLimit=3.0,

        tileGridSize=(8, 8)
    )

    cl = clahe.apply(l)

    enhanced_lab = cv2.merge((cl, a, b))

    ela = cv2.cvtColor(
        enhanced_lab,
        cv2.COLOR_LAB2BGR
    )

    return ela

# =====================================================
# REFINE MASK
# =====================================================

def refine_mask(ela_image):

    gray = cv2.cvtColor(
        ela_image,
        cv2.COLOR_BGR2GRAY
    )

    blur = cv2.GaussianBlur(
        gray,
        (9, 9),
        0
    )

    _, mask = cv2.threshold(

        blur,

        70,

        255,

        cv2.THRESH_BINARY
    )

    kernel = np.ones((5, 5), np.uint8)

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    contours, _ = cv2.findContours(

        mask,

        cv2.RETR_EXTERNAL,

        cv2.CHAIN_APPROX_SIMPLE
    )

    clean_mask = np.zeros_like(mask)

    for cnt in contours:

        area = cv2.contourArea(cnt)

        if area > 80:

            cv2.drawContours(

                clean_mask,

                [cnt],

                -1,

                255,

                -1
            )

    return clean_mask

# =====================================================
# ANALYZE REGIONS
# =====================================================

def analyze_regions(
    mask,
    ela_gray
):

    contours, _ = cv2.findContours(

        mask,

        cv2.RETR_EXTERNAL,

        cv2.CHAIN_APPROX_SIMPLE
    )

    suspicious_regions = []

    total_score = 0

    for cnt in contours:

        x, y, w, h = cv2.boundingRect(cnt)

        area = w * h

        if area < 100:

            continue

        region = ela_gray[y:y+h, x:x+w]

        mean_intensity = np.mean(region)

        if mean_intensity > 20:

            suspicious_regions.append({

                "x": int(x),

                "y": int(y),

                "w": int(w),

                "h": int(h),

                "score": float(mean_intensity)
            })

            total_score += mean_intensity

    return suspicious_regions, min(
        int(total_score / 10),
        100
    )

# =====================================================
# DRAW BOXES
# =====================================================

def draw_boxes(
    image,
    regions
):

    for region in regions:

        x = region["x"]
        y = region["y"]
        w = region["w"]
        h = region["h"]

        cv2.rectangle(

            image,

            (x, y),

            (x + w, y + h),

            (0, 0, 255),

            2
        )

    return image

# =====================================================
# CREATE OVERLAY
# =====================================================

def create_overlay(
    original_image,
    mask
):

    heatmap = cv2.applyColorMap(
        mask,
        cv2.COLORMAP_JET
    )

    overlay = cv2.addWeighted(

        original_image,

        0.75,

        heatmap,

        0.25,

        0
    )

    return overlay

# =====================================================
# MAIN PIPELINE
# =====================================================

def run_ela_detection(image_path):

    filename = os.path.basename(
        image_path
    )

    original = cv2.imread(image_path)

    ela_image = perform_ela(image_path)

    ela_gray = cv2.cvtColor(
        ela_image,
        cv2.COLOR_BGR2GRAY
    )

    mask = refine_mask(
        ela_image
    )

    suspicious_regions, ela_score = analyze_regions(

        mask,

        ela_gray
    )

    overlay = create_overlay(
        original,
        mask
    )

    boxed = draw_boxes(
        original.copy(),
        suspicious_regions
    )

    ela_output_path = save_output(

        ela_image,

        "ela",

        filename
    )

    mask_output_path = save_output(

        mask,

        "mask",

        filename
    )

    overlay_output_path = save_output(

        overlay,

        "overlay",

        filename
    )

    boxed_output_path = save_output(

        boxed,

        "overlay",

        f"boxed_{filename}"
    )

    return {

        "module": "ela",

        "score": ela_score,

        "verdict": get_verdict(
            ela_score
        ),

        "images": {

            "ela": ela_output_path,

            "mask": mask_output_path,

            "overlay": overlay_output_path,

            "boxed": boxed_output_path
        },

        "regions_detected": len(
            suspicious_regions
        ),

        "regions": suspicious_regions
    }