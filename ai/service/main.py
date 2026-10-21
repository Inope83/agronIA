from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings

app = FastAPI(title="Agronia AI Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WEIGHTS_DIR = Path(__file__).resolve().parent.parent / "weights"
CLASSES_PATH = Path(__file__).resolve().parent.parent / "classes.json"


class Settings(BaseSettings):
    model_path: str = ""
    confidence_threshold: float = 0.6
    image_size: int = 224


settings = Settings()


class PredictResponse(BaseModel):
    status: str
    prediction: dict[str, Any] | None = None
    message: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_path": settings.model_path or None,
        "weights_dir": str(WEIGHTS_DIR),
        "has_classes": CLASSES_PATH.exists(),
    }


@app.post("/predict", response_model=PredictResponse)
async def predict(file: UploadFile = File(...)):
    model_path = settings.model_path or os.getenv("AI_MODEL_PATH", "")
    if not model_path or not Path(model_path).is_file():
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "model_unavailable",
                    "message": "AI_MODEL_PATH belum diatur atau berkas model tidak ditemukan.",
                }
            },
        )
    # Belum ada model sungguhan, jadi kita tetap jujur seperti di Django
    raise HTTPException(
        status_code=503,
        detail={
            "error": {
                "code": "model_unavailable",
                "message": "Model AI belum di-load. Isi weights/ dan classes.json sesuai dokumentasi.",
            }
        },
    )


@app.get("/")
def root():
    return {"service": "agronia-ai", "docs": "/docs"}
