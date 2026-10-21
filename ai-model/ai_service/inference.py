"""Lapisan inferensi AI.

Modul ini menyediakan antarmuka yang stabil antara Django dan model
computer vision, sesuai `docs/architecture.md` bagian "AI Inference
Component" dan `docs/ai-model.md` bagian "Integration with Django".

Yang penting dipahami:

- **Belum ada model sungguhan di repo ini.** Dataset dan bobot model belum
  dipilih (lihat `docs/dataset.md`). Karena itu `predict()` akan raising
  `ModelUnavailable` sampai `AI_MODEL_PATH` menunjuk berkas bobot yang
  benar-benar ada.
- **Tidak ada hasil tebakan.** `predict()` tidak pernah mengembalikan
  label penyakit bila model tidak dapat dijalankan.
- Model dimuat sekali lalu dipakai ulang, bukan dimuat ulang tiap permintaan.
- Preprocessing gambar memakai Pillow dan bisa diuji tanpa model.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from PIL import Image, UnidentifiedImageError

from ai_service.exceptions import (
    InferenceError,
    ModelUnavailable,
    UnsupportedClass,
    UnsupportedInput,
)
from ai_service.registry import ClassRegistry

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Prediction:
    """Hasil inferensi yang sudah dipetakan ke kelas terdaftar."""

    class_id: str
    label: str
    confidence: float
    model_version: str
    is_confident: bool

    def to_dict(self) -> dict:
        """Ubah hasil menjadi dict siap dikirim ke API."""
        return {
            "class_id": self.class_id,
            "label": self.label,
            "confidence": self.confidence,
            "model_version": self.model_version,
            "is_confident": self.is_confident,
        }


class InferenceService:
    """Pembungkus pemuatan model dan proses inferensi.

    Contoh pemakaian::

        service = InferenceService()
        try:
            prediction = service.predict(image)
        except ModelUnavailable:
            ...
    """

    def __init__(
        self,
        model_path: str | Path | None = None,
        threshold: float | None = None,
        registry: ClassRegistry | None = None,
    ) -> None:
        self._model_path = str(model_path if model_path is not None else settings.AI_MODEL_PATH)
        self._threshold = (
            float(threshold if threshold is not None else settings.AI_CONFIDENCE_THRESHOLD)
        )
        self._registry = registry if registry is not None else ClassRegistry.load()
        self._model = None

    # -- Properti ---------------------------------------------------------

    @property
    def registry(self) -> ClassRegistry:
        """Daftar kelas yang dikenali model."""
        return self._registry

    @property
    def threshold(self) -> float:
        """Ambang confidence minimum agar hasil dianggap meyakinkan."""
        return self._threshold

    @property
    def is_available(self) -> bool:
        """True bila model tersedia dan daftar kelas tidak kosong."""
        return not self._registry.is_empty and self._model_file_exists()

    # -- Pretreatment -----------------------------------------------------

    def preprocess(self, image: Image.Image) -> "Image.Image":
        """Siapkan gambar sesuai kontrak input model.

        Ukuran dan normalisasi diambil dari `settings.AI_IMAGE_SIZE`.
        Nilai ini wajib dibuat sama dengan saat training.
        """
        size = int(settings.AI_IMAGE_SIZE)
        if size <= 0:
            raise UnsupportedInput("Ukuran input model tidak valid.")

        if image.mode != "RGB":
            image = image.convert("RGB")

        return image.resize((size, size), Image.Resampling.BILINEAR)

    # -- Inferensi --------------------------------------------------------

    def predict(self, image: Image.Image) -> Prediction:
        """Jalankan inferensi pada satu gambar.

        Melempar:
            ModelUnavailable: model tidak ada atau tidak bisa dimuat.
            UnsupportedInput: gambar tidak bisa diproses.
            UnsupportedClass: hasil model di luar daftar kelas terdaftar.
        """
        model = self._load_model()
        classes = self._registry.classes

        if not classes:
            raise ModelUnavailable(
                "Daftar kelas model belum diisi, sehingga analisis belum bisa dijalankan."
            )

        prepared = self.preprocess(image)
        probabilities = self._run(model, prepared)

        if len(probabilities) != len(classes):
            raise UnsupportedClass(
                "Jumlah keluaran model tidak cocok dengan daftar kelas yang terdaftar."
            )

        index = max(range(len(probabilities)), key=probabilities.__getitem__)
        confidence = float(probabilities[index])
        class_id = classes[index]

        if not self._registry.contains(class_id):
            raise UnsupportedClass(f"Kelas hasil inferensi tidak dikenal: {class_id}")

        return Prediction(
            class_id=class_id,
            label=class_id,
            confidence=confidence,
            model_version=self._registry.model_version,
            is_confident=confidence >= self._threshold,
        )

    # -- Internal ---------------------------------------------------------

    def _model_file_exists(self) -> bool:
        """Cek apakah berkas bobot model benar-benar ada di disk."""
        if not self._model_path:
            return False
        return Path(self._model_path).is_file()

    def _load_model(self):
        """Muat bobot model sekali lalu simpan untuk dipakai ulang."""
        if self._model is not None:
            return self._model

        if not self._model_path:
            raise ModelUnavailable(
                "AI_MODEL_PATH belum diatur, sehingga model tidak dapat dimuat."
            )

        if not self._model_file_exists():
            raise ModelUnavailable(
                f"Berkas model tidak ditemukan di: {self._model_path}"
            )

        try:
            import torch
        except ImportError as exc:
            raise ModelUnavailable(
                "PyTorch belum terpasang pada environment ini, sehingga model "
                "tidak dapat dimuat. Lihat docs/ai-model.md bagian instalasi."
            ) from exc

        try:
            model = torch.load(self._model_path, map_location="cpu", weights_only=False)
        except Exception as exc:  # noqa: BLE001 - setiap kegagalan dimuat harus dikontrol
            raise ModelUnavailable(
                f"Berkas model tidak dapat dimuat: {self._model_path}"
            ) from exc

        if hasattr(model, "eval"):
            model.eval()

        self._model = model
        logger.info("Model AI dimuat dari %s", self._model_path)
        return self._model

    def _run(self, model, image: Image.Image) -> list[float]:
        """Jalankan model dan kembalikan daftar probability."""
        try:
            import torch
            from torchvision import transforms
        except ImportError as exc:
            raise ModelUnavailable(
                "PyTorch/torchvision belum terpasang pada environment ini."
            ) from exc

        size = int(settings.AI_IMAGE_SIZE)
        to_tensor = transforms.ToTensor()
        normalise = transforms.Normalize(
            mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
        )

        try:
            batch = normalise(to_tensor(image)).unsqueeze(0)
            with torch.no_grad():
                outputs = model(batch)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
        except Exception as exc:  # noqa: BLE001 - kegagalan inferensi harus dikontrol
            raise InferenceError("Model gagal menjalankan inferensi.") from exc

        return [float(value) for value in probabilities.tolist()]


def load_image(file_obj) -> Image.Image:
    """Baca berkas gambar dengan Pillow dan kembalikan objek Image."""
    try:
        image = Image.open(file_obj)
        image.load()
    except UnidentifiedImageError as exc:
        raise UnsupportedInput("Berkas yang diunggah bukan gambar yang valid.") from exc
    except OSError as exc:
        raise UnsupportedInput("Gambar tidak dapat dibaca.") from exc

    return image
