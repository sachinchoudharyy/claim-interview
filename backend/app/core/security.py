from jose import jwt
from datetime import datetime, timedelta
from app.core.config import JWT_SECRET

ALGORITHM = "HS256"


def create_token(user_id: str):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)