"""Pengaturan untuk environment production.

Semua konfigurasi sensitif dibaca dari environment variable. Startup akan
dihentikan lebih dulu bila konfigurasi wajib tidak lengkap, supaya aplikasi
tidak pernah berjalan dengan secret bawaan di server.
"""

from __future__ import annotations

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import ALLOWED_HOSTS as _BASE_ALLOWED_HOSTS
from .base import DEBUG as _BASE_DEBUG
from .base import SECRET_KEY as _BASE_SECRET_KEY

if not _BASE_SECRET_KEY:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY wajib diisi pada environment production. "
        "Salin .env.example menjadi .env lalu isi nilainya."
    )

if _BASE_DEBUG:
    raise ImproperlyConfigured("DJANGO_DEBUG harus False pada environment production.")

if not _BASE_ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS wajib diisi pada environment production."
    )

SECRET_KEY = _BASE_SECRET_KEY
DEBUG = False
ALLOWED_HOSTS = list(_BASE_ALLOWED_HOSTS)

# --- Keamanan transport -------------------------------------------------

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- Penyimpanan media privat -------------------------------------------

# Berkas unggahan pengguna tidak boleh bisa diakses publik.
# Pada production, MEDIA_ROOT harus berada di luar direktori yang dilayani
# web server secara langsung dan diakses lewat view yang memeriksa izin.
