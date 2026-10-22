"""FastAPI inference service untuk model penyakit padi Agronia."""

from __future__ import annotations

import io
import json
import os
import threading
from pathlib import Path
from typing import Any

os.environ.setdefault("KERAS_BACKEND", "torch")

import keras
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

app = FastAPI(title="Agronia AI Service", version="1.0.0")

PROJECT_DIR = Path(__file__).resolve().parent.parent
CLASSES_PATH = PROJECT_DIR / "classes.json"
MAX_IMAGE_BYTES = 15 * 1024 * 1024
_INFERENCE_LOCK = threading.Lock()


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


class ModelState:
    def __init__(self) -> None:
        self.model: Any | None = None
        self.classes: list[dict[str, Any]] = []
        self.version: str | None = None
        self.image_size = settings.image_size
        self.error: str | None = None
        self._load()

    def _load(self) -> None:
        if not settings.model_path.strip():
            self.error = "AI_MODEL_PATH belum diatur."
            return

        model_path = Path(settings.model_path.strip())
        if not model_path.is_absolute():
            model_path = PROJECT_DIR / model_path
        if not model_path.is_file():
            self.error = "Berkas model tidak ditemukan."
            return
        if not CLASSES_PATH.is_file():
            self.error = "classes.json tidak ditemukan."
            return

        try:
            payload = json.loads(CLASSES_PATH.read_text(encoding="utf-8"))
            classes = payload.get("classes")
            if not isinstance(classes, list) or not classes:
                raise ValueError("daftar classes kosong")
            classes = sorted(classes, key=lambda item: int(item["index"]))
            expected_indexes = list(range(len(classes)))
            if [int(item["index"]) for item in classes] != expected_indexes:
                raise ValueError("index classes harus berurutan dari 0")
            for item in classes:
                if not item.get("class_id") or not item.get("name"):
                    raise ValueError("class_id dan name wajib diisi")

            model = keras.models.load_model(model_path)
            output_classes = int(model.output_shape[-1])
            if output_classes != len(classes):
                raise ValueError(
                    "output model "
                    f"({output_classes}) tidak cocok dengan classes ({len(classes)})"
                )

            self.model = model
            self.classes = classes
            self.version = str(payload.get("model_version") or model_path.stem)
            self.image_size = int(payload.get("image_size") or settings.image_size)
        except Exception as exc:
            self.error = f"Model gagal dimuat: {exc}"


state = ModelState()


def _decode_image(data: bytes) -> np.ndarray:
    with Image.open(io.BytesIO(data)) as image:
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        image = image.resize(
            (state.image_size, state.image_size), Image.Resampling.BILINEAR
        )
        return np.asarray(image, dtype=np.float32)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_available": state.model is not None,
        "classes_registered": bool(state.classes),
        "model_version": state.version,
        "detail": state.error,
    }


@app.post("/predict", response_model=PredictResponse)
def predict(file: UploadFile = File(...)):
    if state.model is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "model_unavailable",
                    "message": state.error or "Model AI belum tersedia.",
                }
            },
        )

    data = file.file.read(MAX_IMAGE_BYTES + 1)
    if not data:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "invalid_image",
                    "message": "Berkas gambar kosong.",
                }
            },
        )
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=413,
            detail={
                "error": {
                    "code": "invalid_image",
                    "message": "Ukuran gambar terlalu besar.",
                }
            },
        )

    try:
        image_array = _decode_image(data)
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "invalid_image",
                    "message": "Berkas bukan gambar yang valid.",
                }
            },
        ) from exc

    with _INFERENCE_LOCK:
        probabilities = state.model.predict(image_array[None, ...], verbose=0)[0]

    if not np.isfinite(probabilities).all():
        raise HTTPException(
            status_code=502,
            detail={
                "error": {
                    "code": "inference_failed",
                    "message": "Model menghasilkan nilai yang tidak valid.",
                }
            },
        )

    index = int(np.argmax(probabilities))
    class_info = state.classes[index]
    confidence = float(probabilities[index])
    display_name = class_info.get("name_id") or class_info["name"]

    return PredictResponse(
        status="ok",
        prediction={
            "class_id": class_info["class_id"],
            "confidence": round(confidence, 4),
            "model_version": state.version,
        },
        message=f"Prediksi: {display_name}.",
    )


@app.get("/")
def root():
    return {
        "service": "agronia-ai",
        "model_version": state.version,
        "docs": "/docs",
    }
