import os
import uuid
import tempfile
import requests
import fitz

from app.db.supabase_client import supabase

# IMPORT PIPELINE
from fraud_detection_system.core.pipeline import run_pipeline


def analyze_document_from_url(file_url: str):

    try:

        # ==========================================
        # DOWNLOAD FILE TEMPORARILY
        # ==========================================

        response = requests.get(file_url)

        if response.status_code != 200:
            return {
                "success": False,
                "error": "Unable to download document"
            }

        is_pdf = ".pdf" in file_url.lower()

        suffix = ".pdf" if is_pdf else ".jpg"

        if ".png" in file_url.lower():
            suffix = ".png"

        temp_filename = f"{uuid.uuid4().hex}{suffix}"

        temp_path = os.path.join(
            tempfile.gettempdir(),
            temp_filename
        )

        with open(temp_path, "wb") as f:
            f.write(response.content)

        # ==========================================
        # PDF → IMAGE
        # ==========================================

        if is_pdf:

            pdf_doc = fitz.open(temp_path)

            page = pdf_doc.load_page(0)

            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

            image_path = os.path.join(
                tempfile.gettempdir(),
                f"{uuid.uuid4().hex}.png"
            )

            pix.save(image_path)

            pdf_doc.close()

            results = run_pipeline(image_path)

            if os.path.exists(image_path):
                os.remove(image_path)

        else:

            results = run_pipeline(temp_path)

        # ==========================================
        # CLEANUP
        # ==========================================

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return results

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }