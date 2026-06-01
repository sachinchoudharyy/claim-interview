import cv2
import numpy as np

# =====================================================
# NORMALIZE HEATMAP
# =====================================================

def normalize_heatmap(mask):

    mask = mask - np.min(mask)

    if np.max(mask) != 0:

        mask = mask / np.max(mask)

    mask = (mask * 255).astype(
        np.uint8
    )

    return mask

# =====================================================
# REFINE MASK
# =====================================================

def refine_mask(mask):

    blur = cv2.GaussianBlur(

        mask,

        (7, 7),

        0
    )

    _, binary = cv2.threshold(

        blur,

        60,

        255,

        cv2.THRESH_BINARY
    )

    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    binary = cv2.morphologyEx(

        binary,

        cv2.MORPH_CLOSE,

        kernel
    )

    return binary

# =====================================================
# SCORE
# =====================================================

def calculate_score(mask):

    suspicious_pixels = np.sum(
        mask > 0
    )

    total_pixels = (
        mask.shape[0]
        *
        mask.shape[1]
    )

    ratio = suspicious_pixels / total_pixels

    score = min(
        int(ratio * 400),
        100
    )

    return score

# =====================================================
# OVERLAY
# =====================================================

def create_overlay(
    original,
    heatmap
):

    color_map = cv2.applyColorMap(

        heatmap,

        cv2.COLORMAP_JET
    )

    overlay = cv2.addWeighted(

        original,

        0.7,

        color_map,

        0.3,

        0
    )

    return overlay