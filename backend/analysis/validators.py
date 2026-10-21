"""Validasi berkas gambar yang diunggah pengguna.

Aturan yang diterapkan (lihat `docs/security.md` bagian "File Upload
Security" dan `docs/api.md` bagian "Validation Requirements"):

- Ukuran berkas dibatasi.
- Format ditentukan dari isi berkas, bukan dari ekstensi atau MIME type
  yang dikirim klien.
- Gambar harus benar-benar bisa dibaca.
- Dimensi dibatasi agar gambar beresolusi sangat besar (decompression bomb)
  tidak menghabiskan memori server.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

#: Format gambar yang diterima.
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}

#: Dimensi minimum. Makin kecil makin tidak berguna sebagai bahan analisis.
MIN_IMAGE_DIMENSION = 64

#: Batas jumlah piksel, mencegah decompression bomb.
MAX_IMAGE_PIXELS = 40_000_000


def validate_image_file(file_obj) -> None:
    """Validasi satu berkas gambar.

    Melempar `django.core.exceptions.ValidationError` bila berkas tidak
    memenuhi aturan.
    """
    if file_obj is None:
        raise ValidationError("Berkas gambar wajib diunggah.", code="image_required")

    size = getattr(file_obj, "size", None)
    max_size = settings.MAX_UPLOAD_SIZE_BYTES
    if size is not None and size > max_size:
        raise ValidationError(
            f"Ukuran file melebihi batas {settings.MAX_UPLOAD_SIZE_MB} MB.",
            code="file_too_large",
        )

    if size is not None and size == 0:
        raise ValidationError("Berkas gambar kosong.", code="image_empty")

    try:
        image = Image.open(file_obj)
        image.verify()
    except UnidentifiedImageError:
        raise ValidationError(
            "Berkas yang diunggah bukan gambar yang valid.",
            code="unsupported_image",
        )
    except (OSError, SyntaxError) as exc:
        raise ValidationError(
            "Gambar tidak dapat dibaca atau rusak.",
            code="corrupt_image",
        ) from exc

    # verify() menutup file, jadi perlu dibuka ulang untuk cek metadata.
    try:
        file_obj.seek(0)
    except (AttributeError, OSError):
        pass

    try:
        image = Image.open(file_obj)
        image_format = image.format
        width, height = image.size
    except (UnidentifiedImageError, OSError, SyntaxError) as exc:
        raise ValidationError(
            "Gambar tidak dapat dibaca atau rusak.",
            code="corrupt_image",
        ) from exc

    if image_format not in ALLOWED_IMAGE_FORMATS:
        supported = ", ".join(sorted(ALLOWED_IMAGE_FORMATS))
        raise ValidationError(
            f"Format gambar tidak didukung. Gunakan format: {supported}.",
            code="unsupported_image_format",
        )

    if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
        raise ValidationError(
            f"Resolusi gambar terlalu kecil. Minimal {MIN_IMAGE_DIMENSION} piksel per sisi.",
            code="image_too_small",
        )

    if width * height > MAX_IMAGE_PIXELS:
        raise ValidationError(
            "Dimensi gambar terlalu besar untuk diproses.",
            code="image_too_large",
        )
