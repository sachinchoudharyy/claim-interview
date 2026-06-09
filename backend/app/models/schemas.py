from pydantic import BaseModel, validator
from typing import Optional
import re


# ---------------- AUTH ----------------

class RegisterRequest(BaseModel):

    phone_number: str
    name: str
    password: str
    confirm_password: str

    @validator("phone_number")
    def validate_phone(cls, v):

        if not re.fullmatch(r"\d{10}", v):
            raise ValueError(
                "Phone number must be exactly 10 digits"
            )

        return v

    @validator("name")
    def validate_name(cls, v):

        v = v.strip()

        if len(v) < 2:
            raise ValueError(
                "Name must be at least 2 characters"
            )

        return v

    @validator("password")
    def validate_password(cls, v):

        if len(v) < 8:
            raise ValueError(
                "Password must be at least 8 characters"
            )

        return v

    @validator("confirm_password")
    def passwords_match(
        cls,
        v,
        values
    ):

        if "password" in values:

            if v != values["password"]:

                raise ValueError(
                    "Passwords do not match"
                )

        return v

class LoginRequest(BaseModel):

    phone_number: str
    password: str

    @validator("phone_number")
    def validate_phone(cls, v):

        if not re.fullmatch(r"\d{10}", v):
            raise ValueError(
                "Phone number must be exactly 10 digits"
            )

        return v

# ---------------- CASE ----------------

class CaseCreate(BaseModel):
    case_id: str
    claim_type: str
    user_id: str
    investigator_name: Optional[str] = None  # ✅ NEW


# ---------------- INTERVIEW ----------------

class InterviewStart(BaseModel):
    case_uuid: str
    category: Optional[str]
    language: str