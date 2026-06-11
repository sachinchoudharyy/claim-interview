from fastapi import APIRouter
from app.db.supabase_client import supabase

from app.services.document_fraud_service import (
    analyze_document_from_url
)

router = APIRouter(prefix="/document-fraud")


@router.post("/analyze/{document_id}")
def analyze_document(document_id: str):

    try:

        # ==========================================
        # FETCH DOCUMENT
        # ==========================================

        res = supabase.table("documents") \
            .select("*") \
            .eq("id", document_id) \
            .single() \
            .execute()

        if not res.data:
            return {
                "success": False,
                "error": "Document not found"
            }

        document = res.data

        file_url = document["file_url"]

        # ==========================================
        # RUN ANALYSIS
        # ==========================================

        result = analyze_document_from_url(
            document
        )

        return result

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }