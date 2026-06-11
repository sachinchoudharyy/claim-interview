from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os

from app.api.auth_routes import router as auth_router
from app.api.case_routes import router as case_router
from app.api.interview_routes import router as interview_router
from app.api.interview_ws import router as interview_ws_router
from app.api.upload_video import router as upload_router
from app.api.document_routes import router as document_router
from app.api.admin_routes import router as admin_router

from app.api.document_fraud_routes import router as document_fraud_router
from app.api.statement_analysis_routes import router as statement_analysis_router

app = FastAPI()

os.makedirs("outputs/ela", exist_ok=True)
os.makedirs("outputs/mask", exist_ok=True)
os.makedirs("outputs/overlay", exist_ok=True)
os.makedirs("outputs/heatmap", exist_ok=True)
os.makedirs("outputs/report", exist_ok=True)
os.makedirs("outputs/debug", exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/outputs",
    StaticFiles(
        directory="fraud_detection_system/storage/outputs"
    ),
    name="outputs"
)


app.include_router(auth_router)
app.include_router(case_router)
app.include_router(interview_router)
app.include_router(interview_ws_router)
app.include_router(upload_router)
app.include_router(document_router)
app.include_router(admin_router, prefix="/admin")

app.include_router(document_fraud_router)
app.include_router(statement_analysis_router)

from app.api.liveness_routes import router as liveness_router
app.include_router(liveness_router)