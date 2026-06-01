import random
from datetime import datetime, timedelta
from app.db.supabase_client import supabase
from app.core.security import create_token

from app.services.case_service import auto_assign_cases_to_user

from app.services.case_log_service import log_case_event

# ---------------- REGISTER ----------------
def register_user(phone_number, name):

    existing = supabase.table("users")\
        .select("*")\
        .eq("phone_number", phone_number)\
        .execute()

    if existing.data:
        return existing.data[0]

    result = supabase.table("users").insert({
        "phone_number": phone_number,
        "name": name,
        "role": "investigator"   # ✅ DEFAULT ROLE
    }).execute()

    return result.data[0]


# ---------------- SEND OTP ----------------
def send_otp(phone_number):

    otp = str(random.randint(100000, 999999))

    expires_at = datetime.utcnow() + timedelta(minutes=5)

    supabase.table("otp_codes")\
        .delete()\
        .eq("phone_number", phone_number)\
        .execute()

    supabase.table("otp_codes").insert({
        "phone_number": phone_number,
        "otp": otp,
        "expires_at": expires_at.isoformat()
    }).execute()

    print(f"OTP for {phone_number}: {otp}")

    return {"message": "OTP sent"}


# ---------------- VERIFY OTP ----------------
def verify_otp(phone_number, otp):

    result = supabase.table("otp_codes")\
        .select("*")\
        .eq("phone_number", phone_number)\
        .eq("otp", otp)\
        .execute()

    if not result.data:
        return {"error": "Invalid OTP"}

    record = result.data[0]

    if datetime.utcnow() > datetime.fromisoformat(record["expires_at"]):
        return {"error": "OTP expired"}

    supabase.table("otp_codes")\
        .delete()\
        .eq("phone_number", phone_number)\
        .execute()

    user_res = supabase.table("users")\
        .select("*")\
        .eq("phone_number", phone_number)\
        .execute()

    if not user_res.data:
        return {"error": "User not found"}

    user = user_res.data[0]
    token = create_token(user["id"])

    return {
        "user": user,
        "token": token
    }


# ---------------- LOGIN (NEW) ----------------
def login_user(phone_number):

    result = supabase.table("users") \
        .select("*") \
        .eq("phone_number", phone_number) \
        .execute()

    if not result.data:
        return {"error": "User not found"}

    user = result.data[0]
    if not user.get("role"):
     user["role"] = "investigator"

    # 🔥 SAFE AUTO ASSIGN (NON-BREAKING)
    try:
        user_name = (user.get("name") or "").strip().lower()

        if user_name:
            cases = supabase.table("cases") \
                .select("id, investigator_name, assigned_user_id") \
                .is_("assigned_user_id", None) \
                .execute()

            updated_count = 0

            for case in cases.data:
                inv_name = case.get("investigator_name")

                if not inv_name:
                    continue

                if inv_name.strip().lower() == user_name:
                    supabase.table("cases") \
                        .update({"assigned_user_id": user["id"]}) \
                        .eq("id", case["id"]) \
                        .execute()

                    # ✅ NEW LOG (SAFE)
                    log_case_event(
                        case["id"],
                        "CASE_ASSIGNED",
                        f"Assigned to {user['name']}",
                        user["name"]
                    )

                    updated_count += 1

            print(f"✅ AUTO-ASSIGNED CASES: {updated_count}")

    except Exception as e:
        print("❌ Auto-assign error:", e)

    token = create_token(user["id"])

    return {
        "user": user,
        "token": token
    }