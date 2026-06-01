from app.db.supabase_client import supabase
from app.services.location_service.location_service  import reverse_geocode
from app.services.location_service.location_validator import validate_location
from app.services.case_log_service import log_case_event


def start_interview(case_id, category, language, location, subcategory=None, subcategory_detail=None, client_ip=None):

    latitude = location.get("latitude")
    longitude = location.get("longitude")

    address_text = None

    # 🔥 LOCATION FRAUD CHECK (SAFE ADD)
    location_result = None

    if location and client_ip:
        try:
            location_result = validate_location(location, client_ip)
        except Exception as e:
            print("Location validation error:", e)

    # reverse geocode if coordinates available
    if latitude and longitude:
        address = reverse_geocode(latitude, longitude)

        address_text = address.get("full_address")

        # 🔥 OPTIONAL (future ready, no break)
        road = address.get("road")
        area = address.get("area")
        district = address.get("district")
    
    subcategory = (subcategory or "").strip().lower() or None

    # ✅ CONVERT case_id → UUID (MATCH DOCUMENTS + VIDEOS)
    # 🔥 ALWAYS CONVERT case_id → UUID
    case = supabase.table("cases") \
        .select("id") \
        .eq("case_id", case_id) \
        .limit(1) \
        .execute()

    if not case.data:
        raise Exception("Case not found")

    case_uuid = case.data[0]["id"]

    

    result = supabase.table("interviews").insert({

        "case_id": case_uuid,   # ✅ ALWAYS UUID
        "category": category,
        "subcategory": subcategory,
        "subcategory_detail": subcategory_detail if subcategory == "others" else None,

        "language": language,

        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "accuracy": location.get("accuracy"),

        "location_text": address_text,
        "location_result": location_result,

        "status": "recording",
        "full_transcript": ""

    }).execute()

    interview = result.data[0]

    # ✅ NEW LOG
    log_case_event(
        case_uuid,
        "INTERVIEW_STARTED",
        "Interview started",
        None,
        subcategory,
        subcategory_detail if subcategory == "others" else None
    )

    return interview


def pause_interview(interview_id):
    supabase.table("interviews") \
        .update({"status": "paused"}) \
        .eq("id", interview_id) \
        .execute()


def resume_interview(interview_id):
    supabase.table("interviews") \
        .update({"status": "recording"}) \
        .eq("id", interview_id) \
        .execute()


from app.services.transcript_service import finalize_transcript


def end_interview(interview_id):

    # mark completed
    supabase.table("interviews") \
        .update({"status": "completed"}) \
        .eq("id", interview_id) \
        .execute()

    # ✅ GET CASE ID (SAFE)
    res = supabase.table("interviews") \
        .select("case_id") \
        .eq("id", interview_id) \
        .execute()

    if res.data:
        case_id = res.data[0]["case_id"]

        # ✅ NEW LOG
        log_case_event(
            case_id,
            "INTERVIEW_COMPLETED",
            "Interview completed",
            None,
            None   # or fetch subcategory if needed
        )

    # ✅ FORCE QA generation
    finalize_transcript(interview_id)