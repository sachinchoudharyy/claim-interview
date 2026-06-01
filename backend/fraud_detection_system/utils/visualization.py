import cv2

# =====================================================
# CREATE OVERLAY
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