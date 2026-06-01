from fastapi import APIRouter
from app.services.case_service import create_case, get_status_report
from app.models.schemas import CaseCreate
from app.db.supabase_client import supabase

from app.services.case_log_service import log_case_event




router = APIRouter(prefix="/cases")
from datetime import datetime


@router.post("/create")
def new_case(data: CaseCreate):

    case = create_case(
        data.user_id,
        data.case_id,
        data.claim_type,
        getattr(data, "category", None),
        getattr(data, "investigator_name", None)  # ✅ NEW
    )

    return case


# ✅ STATIC ROUTES FIRST (IMPORTANT)

from fastapi import Request

@router.get("/all")
def get_all_cases(request: Request):
    """
    Admin only: fetch all cases with optional filters
    """

    try:
        query = supabase.table("cases").select("*")

        # ✅ NEW FILTER (SAFE)
        claim_type = request.query_params.get("claim_type")

        if claim_type:
            query = query.eq("claim_type", claim_type.strip().lower())

        response = query.execute()

        return {"cases": response.data}

    except Exception as e:
        return {"error": str(e)}


@router.get("/my-cases")
def get_my_cases(user_id: str):
    """
    Fetch cases assigned to logged-in user.
    """
    try:
        response = supabase.table("cases") \
            .select("*") \
            .eq("assigned_user_id", user_id) \
            .execute()

        return {"cases": response.data}

    except Exception as e:
        return {"error": str(e)}


@router.get("/by-id/{case_id}")
def get_case_by_id(case_id: str):
    try:
        response = supabase.table("cases") \
            .select("*") \
            .eq("id", case_id) \
            .single() \
            .execute()

        return {"case": response.data}

    except Exception as e:
        return {"error": str(e)}

@router.get("/users")
def get_users():
    try:
        res = supabase.table("users") \
            .select("id, name, role") \
            .eq("role", "investigator") \
            .execute()

        return {"users": res.data}

    except Exception as e:
        return {"error": str(e)}


@router.get("/status-report/{case_id}")
def status_report(case_id: str):
    try:
        report = get_status_report(case_id)
        return report
    except Exception as e:
        return {"error": str(e)}
    

@router.post("/{case_id}/remarks")
def add_remark(case_id: str, data: dict):
    try:
        text = data.get("text")
        created_by = data.get("created_by")

        if not text:
            return {"error": "Text required"}

        # 🔹 convert case_id → UUID
        case = supabase.table("cases") \
            .select("id") \
            .eq("case_id", case_id) \
            .limit(1) \
            .execute()

        if not case.data:
            return {"error": "Case not found"}

        case_uuid = case.data[0]["id"]

        # 🔹 insert remark
        res = supabase.table("remarks").insert({
            "case_id": case_uuid,
            "text": text,
            "created_by": created_by,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        # ✅ LOG EVENT (IMPORTANT)
        log_case_event(
            case_uuid,
            "REMARK_ADDED",
            text,
            created_by
        )

        return res.data[0]

    except Exception as e:
        return {"error": str(e)}


@router.get("/{case_id}/remarks")
def get_remarks(case_id: str):
    try:
        case = supabase.table("cases") \
            .select("id") \
            .eq("case_id", case_id) \
            .limit(1) \
            .execute()

        if not case.data:
            return []

        case_uuid = case.data[0]["id"]

        res = supabase.table("remarks") \
            .select("*") \
            .eq("case_id", case_uuid) \
            .order("created_at", desc=True) \
            .execute()

        return res.data or []

    except Exception as e:
        return []
    
@router.patch("/remarks/{remark_id}")
def update_remark(remark_id: str, data: dict):
    try:
        text = data.get("text")

        if not text:
            return {"error": "Text required"}

        res = supabase.table("remarks") \
            .update({
                "text": text,
                "updated_at": datetime.utcnow().isoformat()
            }) \
            .eq("id", remark_id) \
            .execute()

        return {"message": "Updated", "data": res.data}

    except Exception as e:
        return {"error": str(e)}


# ✅ DYNAMIC ROUTE LAST (VERY IMPORTANT)

@router.get("/{user_id}")
def get_cases(user_id: str):
    """
    Returns:
    - Old cases (user_id)
    - New Excel assigned cases (assigned_user_id)
    SAFE: backward compatible
    """

    try:
        old_cases = supabase.table("cases") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()

        assigned_cases = supabase.table("cases") \
            .select("*") \
            .eq("assigned_user_id", user_id) \
            .execute()

        combined = old_cases.data + assigned_cases.data
        unique_cases = list({c["id"]: c for c in combined}.values())

        return {"cases": unique_cases}

    except Exception as e:
        return {"error": str(e)}


@router.patch("/update/{case_id}")
def update_case(case_id: str, data: dict):

    try:
        print("Updating case:", case_id)
        print("Data:", data)

        response = supabase.table("cases") \
            .update(data) \
            .eq("id", case_id) \
            .execute()

        if not response.data:
            return {
                "error": "No case found or update failed",
                "case_id": case_id
            }

        # ✅ NEW LOG
        log_case_event(
            case_id,
            "CASE_UPDATED",
            "Case fields updated",
            None
        )

        return {
            "message": "Case updated",
            "data": response.data
        }

    except Exception as e:
        return {"error": str(e)}
    

from fastapi import Request

@router.get("/logs/{case_id}")
def get_case_logs(case_id: str, request: Request):
    try:
        # 🔥 CONVERT case_id STRING → UUID
        case = supabase.table("cases") \
            .select("id") \
            .eq("case_id", case_id) \
            .limit(1) \
            .execute()

        if not case.data:
            return []

        case_uuid = case.data[0]["id"]

        # 🔁 UPDATED QUERY USING UUID
        query = supabase.table("case_logs") \
            .select("*") \
            .eq("case_id", case_uuid)

        subcategory = request.query_params.get("subcategory")

        # ✅ APPLY FILTER ONLY IF PROVIDED
        if subcategory:
            query = query.eq("subcategory", subcategory.strip())

        response = query.order("created_at", desc=True).execute()

        return response.data if response.data else []

    except Exception as e:
        return []



@router.post("/reassign/{case_id}")
def reassign_case(case_id: str, data: dict):

    try:
        user_id = data.get("user_id")

        if not user_id:
            return {"error": "user_id required"}

        # 🔍 FETCH USER
        user_res = supabase.table("users") \
            .select("*") \
            .eq("id", user_id) \
            .single() \
            .execute()

        if not user_res.data:
            return {"error": "User not found"}

        user = user_res.data

        # 🔄 UPDATE CASE
        update_res = supabase.table("cases") \
            .update({
                "assigned_user_id": user["id"],
                "investigator_name": user["name"]
            }) \
            .eq("id", case_id) \
            .execute()

        if not update_res.data:
            return {"error": "Case update failed"}

        # ✅ LOG EVENT
        log_case_event(
            case_id,
            "CASE_REASSIGNED",
            f"Reassigned to {user['name']}",
            user["name"]
        )

        return {"message": "Case reassigned"}

    except Exception as e:
        return {"error": str(e)}
    
