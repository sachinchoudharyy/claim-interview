import random
from datetime import datetime, timedelta
from app.db.supabase_client import supabase
from app.core.security import (
    create_token,
    hash_password,
    verify_password
)

from app.services.case_service import auto_assign_cases_to_user

from app.services.case_log_service import log_case_event

# ---------------- REGISTER ----------------
def register_user(
    phone_number,
    name,
    password
):
    if len(phone_number) != 10:
        return {
            "error": "Phone number must be exactly 10 digits"
        }

    if not phone_number.isdigit():
        return {
            "error": "Phone number must contain only digits"
        }

    if len(password) < 8:
        return {
            "error": "Password must be at least 8 characters"
        }

    if len(name.strip()) < 2:
        return {
            "error": "Name is too short"
        }

    existing = (
        supabase
        .table("users")
        .select("*")
        .eq("phone_number", phone_number)
        .execute()
    )

    if existing.data:

        return {
            "error": "Phone number already registered"
        }

    result = (
        supabase
        .table("users")
        .insert({
            "phone_number": phone_number,
            "name": name,
            "password_hash": hash_password(password),
            "role": "investigator"
        })
        .execute()
    )

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
def login_user(
    phone_number,
    password
):

    result = (
        supabase
        .table("users")
        .select("*")
        .eq("phone_number", phone_number)
        .execute()
    )

    if not result.data:

        return {
            "error": "Phone number not registered"
        }

    user = result.data[0]

    password_hash = user.get(
        "password_hash"
    )

    if not password_hash:

        return {
            "error": "User password not configured"
        }

    if not verify_password(
        password,
        password_hash
    ):

        return {
            "error": "Incorrect password"
        }

    token = create_token(
        user["id"]
    )

    return {
        "user": user,
        "token": token
    }