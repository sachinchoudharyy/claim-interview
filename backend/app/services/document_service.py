from app.db.supabase_client import supabase


def save_document(case_uuid, interview_id, file_url, file_type, subcategory=None, subcategory_detail=None):
    return supabase.table("documents").insert({
        "case_id": case_uuid,
        "interview_id": interview_id,
        "file_url": file_url,
        "file_type": file_type,
        "subcategory": subcategory,
        "subcategory_detail": subcategory_detail
    }).execute()


def get_documents(case_uuid):
    res = supabase.table("documents") \
        .select("*") \
        .eq("case_id", case_uuid) \
        .execute()

    return res.data