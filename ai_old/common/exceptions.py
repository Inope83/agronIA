"""Penanganan error yang konsisten untuk seluruh endpoint API.

Format error mengikuti `docs/api.md`:

```json
{
  "error": {
    "code": "invalid_image",
    "message": "Gambar yang dikirim tidak dapat diproses."
  }
}
```

Tidak ada stack trace atau detail internal yang pernah ikut ke respons.
"""

from __future__ import annotations

import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


#: Kode error bawaan untuk setiap status HTTP.
DEFAULT_ERROR_CODES: dict[int, str] = {
    status.HTTP_400_BAD_REQUEST: "invalid_request",
    status.HTTP_401_UNAUTHORIZED: "authentication_required",
    status.HTTP_403_FORBIDDEN: "permission_denied",
    status.HTTP_404_NOT_FOUND: "not_found",
    status.HTTP_405_METHOD_NOT_ALLOWED: "method_not_allowed",
    status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: "file_too_large",
    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: "unsupported_media_type",
    status.HTTP_429_TOO_MANY_REQUESTS: "rate_limit_exceeded",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "internal_server_error",
    status.HTTP_503_SERVICE_UNAVAILABLE: "service_unavailable",
}

#: Pesan bawaan per kode error, ditulis untuk pengguna umum.
DEFAULT_MESSAGES: dict[str, str] = {
    "invalid_request": "Data yang dikirim tidak valid.",
    "authentication_required": "Anda harus masuk terlebih dahulu.",
    "permission_denied": "Anda tidak memiliki izin untuk tindakan ini.",
    "not_found": "Data yang diminta tidak ditemukan.",
    "method_not_allowed": "Metode permintaan tidak didukung.",
    "file_too_large": "Ukuran file terlalu besar.",
    "unsupported_media_type": "Format file tidak didukung.",
    "rate_limit_exceeded": "Terlalu banyak permintaan. Coba lagi nanti.",
    "internal_server_error": "Terjadi kesalahan pada server.",
    "service_unavailable": "Layanan sedang tidak tersedia.",
}

#: Kode bawaan DRF yang digeneralkan agar lebih deskriptif dan seragam.
GENERIC_DRF_CODES: dict[str, str] = {
    "invalid": "invalid_request",
    "parse_error": "invalid_request",
    "required": "invalid_request",
    "not_found": "not_found",
    "not_authenticated": "authentication_required",
    "authentication_failed": "authentication_required",
    "permission_denied": "permission_denied",
    "method_not_allowed": "method_not_allowed",
    "throttled": "rate_limit_exceeded",
    "request_entity_too_large": "file_too_large",
    "unsupported_media_type": "unsupported_media_type",
}


class ModelUnavailable(APIException):
    """Model AI belum tersedia atau gagal dimuat."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Layanan analisis AI sedang tidak tersedia."
    default_code = "model_unavailable"


class UnsupportedCrop(APIException):
    """Jenis tanaman atau kelas yang diminta tidak didukung model."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Jenis tanaman ini belum didukung untuk analisis."
    default_code = "unsupported_crop"


class UnsupportedImage(APIException):
    """Berkas yang diunggah bukan gambar yang bisa diproses."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Berkas yang diunggah bukan gambar yang dapat diproses."
    default_code = "unsupported_image"


def _normalise(exc: Exception) -> Exception:
    """Ubah exception Django menjadi padanan DRF."""
    if isinstance(exc, Http404):
        from rest_framework.exceptions import NotFound

        return NotFound()
    if isinstance(exc, DjangoPermissionDenied):
        return DRFPermissionDenied()
    if isinstance(exc, DjangoValidationError):
        return DRFValidationError(detail=getattr(exc, "messages", [str(exc)]))
    return exc


def _describe(exc: Exception, response) -> tuple[str, str, dict | None]:
    """Tentukan kode, pesan, dan detail tambahan dari sebuah exception."""
    status_code = response.status_code
    code = DEFAULT_ERROR_CODES.get(status_code, "error")
    message = DEFAULT_MESSAGES.get(code, "Permintaan tidak dapat diproses.")
    details: dict | None = None

    if isinstance(exc, APIException):
        default_code = getattr(exc, "default_code", None)
        if default_code:
            code = GENERIC_DRF_CODES.get(default_code, default_code)

        data = response.data
        if isinstance(data, dict):
            detail = data.get("detail")
            if isinstance(detail, str) and detail:
                message = detail
            else:
                details = data
        elif isinstance(data, list):
            message = str(data[0]) if data else message
            details = {"non_field_errors": data}

    return code, message, details


def api_exception_handler(exc, context):
    """Exception handler DRF yang menghasilkan format error konsisten."""
    exc = _normalise(exc)

    response = drf_exception_handler(exc, context)
    if response is None:
        # Exception yang tidak ditangani DRF. Dicatat di log, respons
        # tetap dikembalikan oleh Django sebagai 500 tanpa detail internal.
        logger.exception("Unhandled API exception", exc_info=exc)
        return None

    code, message, details = _describe(exc, response)

    payload: dict[str, dict] = {"error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details

    response.data = payload
    return response
