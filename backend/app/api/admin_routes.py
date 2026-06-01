from fastapi import APIRouter, UploadFile, File
import shutil
import os
from app.services.excel_service import process_excel

router = APIRouter()


@router.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):

    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    process_excel(file_path)

    os.remove(file_path)

    return {"message": "Excel uploaded successfully"}