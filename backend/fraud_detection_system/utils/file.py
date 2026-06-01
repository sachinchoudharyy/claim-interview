import os
import uuid

from fraud_detection_system.config import (
    UPLOAD_DIR,
    TEMP_DIR,
    OUTPUT_DIR,
    ELA_OUTPUT_DIR,
    MASK_OUTPUT_DIR,
    OVERLAY_OUTPUT_DIR,
    HEATMAP_OUTPUT_DIR,
    REPORT_OUTPUT_DIR,
    DEBUG_OUTPUT_DIR
)

# =====================================================
# CREATE DIRECTORIES
# =====================================================

def create_directories():

    directories = [

        UPLOAD_DIR,

        TEMP_DIR,

        OUTPUT_DIR,

        ELA_OUTPUT_DIR,

        MASK_OUTPUT_DIR,

        OVERLAY_OUTPUT_DIR,

        HEATMAP_OUTPUT_DIR,

        REPORT_OUTPUT_DIR,

        DEBUG_OUTPUT_DIR
    ]

    for directory in directories:

        os.makedirs(
            directory,
            exist_ok=True
        )

# =====================================================
# UNIQUE FILENAME
# =====================================================

def generate_filename(original_name):

    extension = os.path.splitext(
        original_name
    )[1]

    return f"{uuid.uuid4().hex}{extension}"

# =====================================================
# RESET OUTPUTS
# =====================================================

def reset_output_folders():

    output_dirs = [

        ELA_OUTPUT_DIR,

        MASK_OUTPUT_DIR,

        OVERLAY_OUTPUT_DIR,

        HEATMAP_OUTPUT_DIR,

        REPORT_OUTPUT_DIR,

        DEBUG_OUTPUT_DIR
    ]

    for directory in output_dirs:

        for file in os.listdir(directory):

            file_path = os.path.join(
                directory,
                file
            )

            try:

                if os.path.isfile(file_path):

                    os.remove(file_path)

            except Exception as e:

                print(
                    f"Error deleting {file_path}: {e}"
                )