from fastapi import APIRouter, UploadFile, File
from app.services.liveness_service.liveness import detect_liveness_from_bytes

router = APIRouter(prefix="/liveness")


@router.post("/check")
async def check_liveness(file: UploadFile = File(...)):
    try:
        video_bytes = await file.read()

        result = detect_liveness_from_bytes(video_bytes)

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        print("LIVENESS ERROR:", e)
        return {
            "success": False,
            "error": str(e)
        }