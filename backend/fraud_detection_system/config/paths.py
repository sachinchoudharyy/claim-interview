import os

# =====================================================
# BASE
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# =====================================================
# STORAGE
# =====================================================

STORAGE_DIR = os.path.join(BASE_DIR, "storage")

UPLOAD_DIR = os.path.join(
    STORAGE_DIR,
    "uploads"
)

TEMP_DIR = os.path.join(
    STORAGE_DIR,
    "temp"
)

OUTPUT_DIR = os.path.join(
    STORAGE_DIR,
    "outputs"
)

# =====================================================
# OUTPUTS
# =====================================================

ELA_OUTPUT_DIR = os.path.join(
    OUTPUT_DIR,
    "ela"
)

MASK_OUTPUT_DIR = os.path.join(
    OUTPUT_DIR,
    "masks"
)

OVERLAY_OUTPUT_DIR = os.path.join(
    OUTPUT_DIR,
    "overlays"
)

HEATMAP_OUTPUT_DIR = os.path.join(
    OUTPUT_DIR,
    "heatmaps"
)

REPORT_OUTPUT_DIR = os.path.join(
    OUTPUT_DIR,
    "reports"
)

DEBUG_OUTPUT_DIR = os.path.join(
    OUTPUT_DIR,
    "debug"
)

# =====================================================
# MODELS
# =====================================================

MODELS_DIR = os.path.join(
    BASE_DIR,
    "models"
)

MANTRANET_MODEL_PATH = os.path.join(
    MODELS_DIR,
    "mantranet",
    "MantraNetv4.pt"
)

IMTFE_MODEL_PATH = os.path.join(
    MODELS_DIR,
    "mantranet",
    "IMTFEv4.pt"
)

ANOMALY_MODEL_PATH = os.path.join(
    MODELS_DIR,
    "mantranet",
    "AnomalyDetectorv4.pt"
)

AI_DETECTION_MODEL_PATH = os.path.join(
    MODELS_DIR,
    "ai_detection",
    "ai_vs_real_detector (1).pth"
)