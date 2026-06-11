from fastapi import APIRouter

from app.db.supabase_client import supabase

from app.services.statement_analysis_service import (
    analyze_statement_from_url
)

router = APIRouter(
    prefix="/statement-analysis",
    tags=["Statement Analysis"]
)


@router.post("/analyze/{document_id}")
def analyze_statement(document_id: str):

    doc = (
        supabase.table("documents")
        .select("*")
        .eq("id", document_id)
        .single()
        .execute()
    )

    if not doc.data:

        return {
            "error":
            "Document not found"
        }

    file_url = doc.data["file_url"]

    result = analyze_statement_from_url(
        file_url
    )

    return result