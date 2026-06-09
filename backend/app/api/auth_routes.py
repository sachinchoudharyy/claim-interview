from fastapi import APIRouter
from app.services.auth_service import (
    register_user,
    send_otp,
    verify_otp,
    login_user
)
from app.models.schemas import RegisterRequest, LoginRequest

router = APIRouter(prefix="/auth")


@router.post("/register")
def register(data: RegisterRequest):

    result = register_user(
        data.phone_number,
        data.name,
        data.password
    )

    return result


@router.post("/send-otp")
def sendotp(data: dict):
    return send_otp(data["phone_number"])


@router.post("/verify-otp")
def verifyotp(data: dict):
    return verify_otp(data["phone_number"], data["otp"])


# ✅ UPDATED LOGIN ROUTE (NOW VALIDATED)
@router.post("/login")
def login(data: LoginRequest):

    result = login_user(
        data.phone_number,
        data.password
    )

    return result