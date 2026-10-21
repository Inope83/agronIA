"""Daftar kelas yang dikenali model.

Sumber kebenaran adalah berkas `ai_service/classes.json`. Daftar itu masih
kosong karena dataset dan bobot model belum dipilih (lihat `docs/dataset.md`
dan `docs/ai-model.md`).

Konsekuensinya: selama daftar kelas kosong, permintaan analisis akan
ditolak dengan `ModelUnavailable`. Aplikasi tidak pernah menebak nama
penyakit saat model belum siap.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CLASSES_FILE = Path(__file__).resolve().parent / "classes.json"


@dataclass(frozen=True)
class ClassRegistry:
    """Kumpulan kelas yang dikenali sebuah versi model."""

    model_version: str
    classes: tuple[str, ...]
    description: str = ""

    @property
    def is_empty(self) -> bool:
        """True bila belum ada kelas yang terdaftar."""
        return not self.classes

    def contains(self, class_id: str) -> bool:
        """Cek apakah sebuah id kelas terdaftar."""
        return class_id in self.classes

    @classmethod
    def load(cls, path: Path | None = None) -> "ClassRegistry":
        """Baca daftar kelas dari berkas JSON."""
        classes_file = path if path is not None else CLASSES_FILE
        if not classes_file.is_file():
            return cls(model_version="none", classes=())

        try:
            payload = json.loads(classes_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Berkas kelas model tidak valid: {classes_file}") from exc

        raw_classes = payload.get("classes") or []
        if not isinstance(raw_classes, list):
            raise ValueError(f"Field 'classes' harus berupa daftar: {classes_file}")

        return cls(
            model_version=str(payload.get("model_version") or "none"),
            classes=tuple(str(item) for item in raw_classes),
            description=str(payload.get("description") or ""),
        )
