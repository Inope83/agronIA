from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

app = FastAPI(title="Agronia AI Service", version="1.0.0")

PROJECT_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_DIR = PROJECT_DIR / "weights"
CLASSES_PATH = PROJECT_DIR / "classes.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AI_",
        env_file=PROJECT_DIR / ".env",
        extra="ignore",
    )

    model_path: str = ""
    image_size: int = 224


settings = Settings()


class PredictResponse(BaseModel):
    status: str
    prediction: dict[str, Any] | None = None
    message: str


def _model_file_available() -> bool:
    return bool(settings.model_path) and Path(settings.model_path).is_file()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_available": _model_file_available(),
        "classes_registered": CLASSES_PATH.exists(),
    }


@app.post("/predict", response_model=PredictResponse)
async def predict(file: UploadFile = File(...)):
    if not _model_file_available():
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "model_unavailable",
                    "message": (
                        "AI_MODEL_PATH belum diatur atau berkas model tidak ditemukan."
                    ),
                }
            },
        )

    raise HTTPException(
        status_code=503,
        detail={
            "error": {
                "code": "model_unavailable",
                "message": (
                    "Model AI belum di-load. Isi weights/ dan classes.json "
                    "sesuai dokumentasi."
                ),
            }
        },
    )


@app.get("/")
def root():
    return {"service": "agronia-ai", "docs": "/docs"}
