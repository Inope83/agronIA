"""Tampilan bersama, termasuk indeks API."""

from __future__ import annotations

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class ApiIndexView(APIView):
    """Daftar endpoint yang tersedia pada versi API ini.

    Berguna sebagai pemeriksaan cepat saat integrasi sisi Flutter.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """Kembalikan daftar endpoint dan versi kontrak."""
        return Response(
            {
                "version": "v1",
                "endpoints": {
                    "auth": {
                        "register": "/api/v1/auth/register/",
                        "login": "/api/v1/auth/login/",
                        "logout": "/api/v1/auth/logout/",
                        "me": "/api/v1/auth/me/",
                    },
                    "agriculture": {
                        "crops": "/api/v1/crops/",
                        "diseases": "/api/v1/diseases/",
                        "resources": "/api/v1/resources/",
                    },
                    "analysis": {
                        "list": "/api/v1/analyses/",
                        "create": "/api/v1/analyses/",
                        "detail": "/api/v1/analyses/{id}/",
                    },
                },
            }
        )
