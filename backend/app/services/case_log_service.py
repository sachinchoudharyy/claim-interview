from app.db.supabase_client import supabase


def log_case_event(case_id, action, description, created_by=None, subcategory=None, subcategory_detail=None):
    try:
        supabase.table("case_logs").insert({
            "case_id": case_id,
            "action": action,
            "description": description,
            "created_by": created_by,
            "subcategory": subcategory,
            "subcategory_detail": subcategory_detail
        }).execute()
    except Exception as e:
        print("CASE LOG ERROR:", e)