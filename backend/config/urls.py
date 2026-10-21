"""Konfigurasi URL utama proyek Agronia.

Semua endpoint API berada di bawah prefiks `/api/v1/` sesuai
`docs/api.md` bagian "API Principles" dan ADR-009.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from common.handlers import not_found, server_error_500
from common.views import ApiIndexView

handler404 = not_found
handler500 = server_error_500

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", ApiIndexView.as_view(), name="api-index"),
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/", include("agriculture.urls")),
    path("api/v1/", include("analysis.urls")),
]

# Catatan: berkas unggahan pengguna TIDAK dilayani lewat `static()`.
# Folder MEDIA_ROOT bersifat privat dan hanya bisa diakses melalui
# endpoint yang memeriksa kepemilikan, misalnya
# `/api/v1/analyses/<id>/image/`. Menambahkan `static(settings.MEDIA_URL, ...)`
# di sini akan membuat gambar bisa dibuka siapa saja yang tahu tautannya,
# melanggar `docs/security.md` bagian "File Upload Security".
