"""Handler error tingkat Django.

Handler ini dipakai untuk memastikan response 404 dan 500 dari endpoint
`/api/` juga memakai format yang sama dengan `common.exceptions`, yaitu
`{"error": {"code": ..., "message": ...}}`. Tanpa handler ini, permintaan
ke URL API yang tidak dikenal akan mengembalikan halaman HTML bawaan
Django, sehingga klien Flutter tidak bisa membacanya.
"""

from __future__ import annotations

import logging

from django.http import HttpResponseNotFound, JsonResponse
from django.views.defaults import page_not_found, server_error

from common.exceptions import DEFAULT_MESSAGES

logger = logging.getLogger(__name__)

#: Prefiks URL yang dianggap sebagai API.
API_PREFIX = "/api/"


def is_api_request(request) -> bool:
    """Cek apakah permintaan datang dari path API."""
    return request.path.startswith(API_PREFIX)


def not_found(request, exception=None):
    """Tangani 404."""
    if is_api_request(request):
        return JsonResponse(
            {"error": {"code": "not_found", "message": DEFAULT_MESSAGES["not_found"]}},
            status=404,
        )
    return page_not_found(request, exception)


def server_error_500(request):
    """Tangani 500 tanpa membocorkan detail internal."""
    if is_api_request(request):
        logger.exception("Unhandled server error on API request")
        return JsonResponse(
            {
                "error": {
                    "code": "internal_server_error",
                    "message": DEFAULT_MESSAGES["internal_server_error"],
                }
            },
            status=500,
        )
    return server_error(request)


__all__ = ["not_found", "server_error_500", "is_api_request", "HttpResponseNotFound"]
