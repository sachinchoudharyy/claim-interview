from fastapi import Request
from fastapi import APIRouter

from app.services.interview_service import (
    start_interview,
    pause_interview,
    resume_interview,
    end_interview
)

router = APIRouter(prefix="/interview")


@router.post("/start")
def start(data: dict, request: Request):

    # ✅ SAFE ACCESS (NO CRASH)
    case_id = data.get("case_id")
    category = data.get("category")
    language = data.get("language")
    location = data.get("location", {})
    subcategory = data.get("subcategory")
    subcategory_detail = data.get("subcategory_detail")

    if subcategory == "others" and not subcategory_detail:
        return {"error": "subcategory_detail required for others"}
    

    # ✅ DEBUG
    print("START DATA:", data)

    if not case_id:
        return {"error": "case_id missing"}

    if not language:
        return {"error": "language missing"}   # VERY IMPORTANT

    client_ip = data.get("client_ip") or request.client.host
    print("CLIENT IP RECEIVED:", client_ip)

    interview = start_interview(
        case_id,
        category,
        language,
        location,
        subcategory,
        subcategory_detail,
        client_ip  # NEW
    )

    return {
        "id": interview["id"],
        "location_text": interview.get("location_text")
    }


@router.post("/pause/{interview_id}")
def pause(interview_id: str):
    pause_interview(interview_id)
    return {"status": "paused"}


@router.post("/resume/{interview_id}")
def resume(interview_id: str):
    resume_interview(interview_id)
    return {"status": "recording"}


@router.post("/end/{interview_id}")
def end(interview_id: str):
    end_interview(interview_id)
    return {"status": "completed"}


from app.db.supabase_client import supabase


from fastapi import Request

@router.get("/by-case/{case_id}")
def get_interview_by_case(case_id: str, request: Request):

    # ✅ GET UUID
    case = supabase.table("cases") \
        .select("id") \
        .eq("case_id", case_id) \
        .limit(1) \
        .execute()

    if not case.data:
        return []

    case_uuid = case.data[0]["id"]

    subcategory = request.query_params.get("subcategory")

    # 🔥 FETCH BOTH (UUID + STRING)
    query = supabase.table("interviews") \
        .select("*") \
        .eq("case_id", case_uuid)

    if subcategory:
        subcategory = subcategory.strip().lower()
        query = query.ilike("subcategory", subcategory)

    result = query.order("created_at", desc=True).execute()

    return result.data or []




@router.patch("/update/{interview_id}")
def update_interview(interview_id: str, data: dict):
    try:
        response = supabase.table("interviews") \
            .update(data) \
            .eq("id", interview_id) \
            .execute()

        if not response.data:
            return {"error": "Update failed"}

        return {"message": "Interview updated"}

    except Exception as e:
        return {"error": str(e)}