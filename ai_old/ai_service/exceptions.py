"""Exception khusus lapisan inferensi AI.

Exception di sini sengaja dipisahkan dari `common.exceptions` supaya lapisan
inferensi tidak bergantung pada lapisan presentasi API.
"""

from __future__ import annotations


class InferenceError(Exception):
    """Kegagalan umum saat menjalankan inferensi."""


class ModelUnavailable(InferenceError):
    """Bobot model tidak ditemukan atau tidak bisa dimuat.

    Dipicu ketika `AI_MODEL_PATH` kosong, berkas model hilang, atau
    framework inferensi (PyTorch/ONNX Runtime) tidak tersedia.
    """


class UnsupportedInput(InferenceError):
    """Gambar di luar rentang yang bisa ditangani model."""


class UnsupportedClass(InferenceError):
    """Kelas hasil inferensi tidak ada di daftar kelas yang terdaftar."""
