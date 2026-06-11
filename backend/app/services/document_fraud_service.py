import os
import uuid
import tempfile
import requests
import fitz

from app.db.supabase_client import supabase

# IMPORT PIPELINE
from fraud_detection_system.core.pipeline import run_pipeline

from fraud_detection_system.modules.face_verification.detector import (
    verify_faces
)

def analyze_document_from_url(document):
    file_url = document["file_url"]

    case_id = document["case_id"]

    verification_doc = (

        supabase.table("documents")

        .select("*")

        .eq("case_id", case_id)

        .eq("subcategory", "verification_photo")

        .limit(1)

        .execute()

    )

    verification_url = None

    if verification_doc.data:

        verification_url = (
            verification_doc.data[0]["file_url"]
        )

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

        verification_temp_path = None

        if verification_url:

            verification_response = requests.get(
                verification_url
            )

            if verification_response.status_code == 200:

                verification_temp_path = os.path.join(
                    tempfile.gettempdir(),
                    f"{uuid.uuid4().hex}.jpg"
                )

                with open(
                    verification_temp_path,
                    "wb"
                ) as vf:

                    vf.write(
                        verification_response.content
                    )

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

        else:

            results = run_pipeline(temp_path)


        # ==========================================
        # FACE VERIFICATION (FOR PDF + IMAGES)
        # ==========================================

        if verification_temp_path:

            compare_path = (
                image_path
                if is_pdf
                else temp_path
            )

            print("Verification Photo Found")
            print("Compare Path:", compare_path)
            print("Verification Path:", verification_temp_path)

            face_result = verify_faces(
                compare_path,
                verification_temp_path
            )

            print("Face Result:", face_result)

            if "modules" not in results:
                results["modules"] = {}

            results["modules"]["face_verification"] = face_result


        # ==========================================
        # PDF CLEANUP
        # ==========================================

        if is_pdf and os.path.exists(image_path):
            os.remove(image_path)

        # ==========================================
        # CLEANUP
        # ==========================================

        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if (
            verification_temp_path
            and
            os.path.exists(
                verification_temp_path
            )
        ):

            os.remove(
                verification_temp_path
            )

        return results

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }