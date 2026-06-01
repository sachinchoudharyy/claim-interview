from fastapi import APIRouter, UploadFile, File, Form
from app.db.supabase_client import supabase
from app.services.document_service import save_document
import uuid
import re
from fastapi import Request

from app.services.case_log_service import log_case_event

router = APIRouter(prefix="/documents")


@router.post("/upload")
async def upload_document(
    case_id: str = Form(...),
    interview_id: str = Form(None),
    subcategory: str = Form(None),  # ✅ ADD
    subcategory_detail: str = Form(None),
    
    file: UploadFile = File(...)
):
    try:
        # read file
        data = await file.read()

        # 🔥 CLEAN FILENAME (avoid unicode / spaces issues)
        clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.filename)
        name = f"{uuid.uuid4()}_{clean_name}"

        # 🔥 FIX PATH (NO double "documents/")
        path = f"{case_id}/{name}"

        # upload to Supabase storage
        supabase.storage.from_("documents").upload(
            path,
            data,
            file_options={"content-type": file.content_type}
        )

        # get public URL
        url = supabase.storage.from_("documents").get_public_url(path)

        # convert case_id → UUID
        case = supabase.table("cases") \
            .select("id") \
            .eq("case_id", case_id) \
            .limit(1) \
            .execute()

        if not case.data:
            return {"error": "Case not found"}

        case_uuid = case.data[0]["id"]

        subcategory = (subcategory or "").strip().lower() or None
        subcategory_detail = (subcategory_detail or "").strip() or None

        # save in DB
        save_document(
            case_uuid,
            interview_id,
            url,
            file.content_type,
            subcategory,
            subcategory_detail if subcategory == "others" else None
        )

        log_case_event(
            case_uuid,
            "DOCUMENT_UPLOADED",
            f"{file.filename} uploaded",
            None,
            subcategory   # ✅ ADD
        )

        return {"url": url}

    except Exception as e:
        print("DOCUMENT UPLOAD ERROR:", e)
        return {"error": "Upload failed"}


@router.get("/{case_id}")
def get_docs(case_id: str, request: Request):

    try:
        case = supabase.table("cases") \
            .select("id") \
            .eq("case_id", case_id) \
            .limit(1) \
            .execute()

        if not case.data:
            return []

        case_uuid = case.data[0]["id"]

        query = supabase.table("documents") \
            .select("*") \
            .eq("case_id", case_uuid)

        subcategory = request.query_params.get("subcategory")

        if subcategory:
            query = query.ilike("subcategory", subcategory)

        res = query.order("created_at", desc=True).execute()

        return res.data

    except Exception as e:
        print("GET DOCUMENT ERROR:", e)
        return []