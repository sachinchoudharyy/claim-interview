import os

import cv2
import torch
import numpy as np

from fraud_detection_system.config import (
    MANTRANET_MODEL_PATH,
    get_verdict
)

from fraud_detection_system.core.outputs import save_output

from fraud_detection_system.modules.mantranet.model import (
    MantraNet
)
from fraud_detection_system.modules.mantranet.processing import (

    normalize_heatmap,

    refine_mask,

    calculate_score,

    create_overlay
)

# =====================================================
# DEVICE
# =====================================================

device = torch.device(

    "cuda"

    if torch.cuda.is_available()

    else "cpu"
)

# =====================================================
# LOAD MODEL
# =====================================================

model = MantraNet()

model.load_state_dict(

    torch.load(

        MANTRANET_MODEL_PATH,

        map_location=device
    )
)

model.to(device)

model.eval()

# =====================================================
# MAIN PIPELINE
# =====================================================

def run_mantranet_detection(
    image_path
):

    filename = os.path.basename(
        image_path
    )

    original = cv2.imread(
        image_path
    )

    original_rgb = cv2.cvtColor(

        original,

        cv2.COLOR_BGR2RGB
    )

    # =====================================================
    # ORIGINAL PREPROCESSING
    # =====================================================

    resized = cv2.resize(

        original_rgb,

        (256, 256)
    )

    img = resized.astype(
        np.float32
    )

    img = img / 255.0

    img = np.transpose(
        img,
        (2, 0, 1)
    )

    tensor = torch.tensor(
        img
    ).float()

    tensor = tensor.unsqueeze(0)

    tensor = tensor.to(device)

    # =====================================================
    # INFERENCE
    # =====================================================

    with torch.no_grad():

        output = model(tensor)

    heatmap = output.squeeze().cpu().numpy()

    # =====================================================
    # NORMALIZATION
    # =====================================================

    heatmap_uint8 = normalize_heatmap(
        heatmap
    )

    # =====================================================
    # RESIZE
    # =====================================================

    heatmap_resized = cv2.resize(

        heatmap_uint8,

        (
            original.shape[1],
            original.shape[0]
        )
    )

    # =====================================================
    # ORIGINAL THRESHOLD
    # =====================================================

    raw_mask = (

        heatmap_resized > 50

    ).astype(np.uint8) * 255

    mask = refine_mask(
        raw_mask
    )

    # =====================================================
    # OVERLAY
    # =====================================================

    overlay = create_overlay(

        original,

        heatmap_resized
    )

    # =====================================================
    # SCORE
    # =====================================================

    score = calculate_score(
        mask
    )

    # =====================================================
    # SAVE OUTPUTS
    # =====================================================

    heatmap_path = save_output(

        heatmap_resized,

        "heatmap",

        f"mantranet_heatmap_{filename}"
    )

    mask_path = save_output(

        mask,

        "mask",

        f"mantranet_mask_{filename}"
    )

    overlay_path = save_output(

        overlay,

        "overlay",

        f"mantranet_overlay_{filename}"
    )

    return {

        "module": "mantranet",

        "score": score,

        "verdict": get_verdict(
            score
        ),

        "images": {

            "heatmap": heatmap_path,

            "mask": mask_path,

            "overlay": overlay_path
        }
    }