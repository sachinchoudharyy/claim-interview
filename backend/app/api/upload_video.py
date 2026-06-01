from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, Request
from app.db.supabase_client import supabase
import uuid
import tempfile

router = APIRouter()


# 🔥 BACKGROUND AI PROCESS (NEW)
def process_ai_pipeline(video_bytes, video_id):
    try:
        from app.services.liveness_service.liveness import detect_liveness_from_bytes
        from app.services.audio_service.audio_pipeline import run_audio_pipeline
        from app.services.fraud_service.fraud_score import compute_fraud_score

        print("BACKGROUND: START AI PIPELINE")

        # 🔹 Liveness
        liveness_result = detect_liveness_from_bytes(video_bytes)

        # 🔹 Audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(video_bytes)
            temp_video_path = tmp.name

        audio_result = run_audio_pipeline(temp_video_path)

        # 🔹 Fraud
        fraud_result = compute_fraud_score(liveness_result, audio_result)

        print("BACKGROUND DONE:", {
            "liveness": liveness_result,
            "audio": audio_result,
            "fraud": fraud_result
        })

        # 🔹 UPDATE DB (IMPORTANT)
        supabase.table("videos").update({
            "liveness_result": liveness_result,
            "audio_result": audio_result,
            "fraud_result": fraud_result
        }).eq("id", video_id).execute()

    except Exception as e:
        print("BACKGROUND PIPELINE ERROR:", e)


@router.post("/upload-video")
async def upload_video(
    background_tasks: BackgroundTasks,
    interview_id: str = Form(...),
    case_id: str = Form(None),
    subcategory: str = Form(default=None),
    subcategory_detail: str = Form(default=None),
    file: UploadFile = File(...)
):
    try:
        data = await file.read()

        # 🔥 CHECK FIRST VIDEO
        existing_videos = supabase.table("videos") \
            .select("id") \
            .eq("interview_id", interview_id) \
            .limit(1) \
            .execute()

        is_first_video = not existing_videos.data

        name = f"{uuid.uuid4()}.webm"

        # ✅ CASE ID RESOLVE (UNCHANGED)
        if not case_id:
            res = supabase.table("interviews") \
                .select("case_id") \
                .eq("id", interview_id) \
                .execute()

            if not res.data:
                return {"error": "Interview not found"}

            case_uuid = res.data[0]["case_id"]
        else:
            case = supabase.table("cases") \
                .select("id") \
                .eq("case_id", case_id) \
                .limit(1) \
                .execute()

            if not case.data:
                return {"error": "Case not found"}

            case_uuid = case.data[0]["id"]

        path = f"{case_uuid}/{interview_id}/{name}"

        # 🔹 Upload video immediately
        supabase.storage.from_("interview-videos") \
            .upload(path, data, {"content-type": "video/webm"})

        url = supabase.storage.from_("interview-videos") \
            .get_public_url(path)

        subcategory = (subcategory or "").strip().lower() or None
        subcategory_detail = (subcategory_detail or "").strip() or None

        if subcategory == "":
            subcategory = None

        # 🔥 INSERT WITHOUT AI RESULTS (IMPORTANT CHANGE)
        insert_res = supabase.table("videos").insert({
            "interview_id": interview_id,
            "case_id": case_uuid,
            "subcategory": subcategory,
            "subcategory_detail": subcategory_detail if subcategory == "others" else None,
            "video_url": url,
            "liveness_result": None,
            "audio_result": None,
            "fraud_result": None
        }).execute()

        video_id = insert_res.data[0]["id"] if insert_res.data else None

        # 🔥 RUN AI IN BACKGROUND (ONLY FIRST CLIP)
        if is_first_video and video_id:
            background_tasks.add_task(process_ai_pipeline, data, video_id)

        print("VIDEO SAVED:", {
            "case_id": case_uuid,
            "subcategory": subcategory
        })

        # 🔥 RETURN IMMEDIATELY (FAST RESPONSE)
        return {"url": url}

    except Exception as e:
        print("VIDEO UPLOAD ERROR:", e)
        return {"error": "Upload failed"}


@router.get("/videos/{case_id}")
def get_videos(case_id: str, request: Request):

    case = supabase.table("cases") \
        .select("id") \
        .eq("case_id", case_id) \
        .limit(1) \
        .execute()

    if not case.data:
        return []

    case_uuid = case.data[0]["id"]

    query = supabase.table("videos") \
        .select("*") \
        .eq("case_id", case_uuid)

    subcategory = request.query_params.get("subcategory")

    if subcategory:
        subcategory = subcategory.strip().lower()
        query = query.ilike("subcategory", subcategory)

    result = query.execute()

    return result.data or []