import os
import cv2

from fraud_detection_system.config import (
    ELA_OUTPUT_DIR,
    MASK_OUTPUT_DIR,
    OVERLAY_OUTPUT_DIR,
    HEATMAP_OUTPUT_DIR,
    REPORT_OUTPUT_DIR,
    DEBUG_OUTPUT_DIR
)

# =====================================================
# OUTPUT MAP
# =====================================================

OUTPUT_MAPPING = {

    "ela": ELA_OUTPUT_DIR,

    "mask": MASK_OUTPUT_DIR,

    "overlay": OVERLAY_OUTPUT_DIR,

    "heatmap": HEATMAP_OUTPUT_DIR,

    "report": REPORT_OUTPUT_DIR,

    "debug": DEBUG_OUTPUT_DIR
}

# =====================================================
# SAVE OUTPUT
# =====================================================

def save_output(
    image,
    category,
    filename
):

    directory = OUTPUT_MAPPING[category]

    output_path = os.path.join(
        directory,
        filename
    )

    cv2.imwrite(
        output_path,
        image
    )

    relative_path = output_path.replace("\\", "/")

    if "storage/outputs/" in relative_path:

        relative_path = relative_path.split(
            "storage/outputs/"
        )[1]

    return f"/outputs/{relative_path}"