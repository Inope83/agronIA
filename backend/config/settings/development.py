"""Pengaturan untuk environment development (lokal).

Dipakai secara bawaan oleh `manage.py` supaya developer tidak perlu
mengatur environment variable apa pun untuk menjalankan proyek.
"""

from __future__ import annotations

from .base import *  # noqa: F401,F403
from .base import ALLOWED_HOSTS as _ENV_ALLOWED_HOSTS
from .base import SECRET_KEY

# Secret key development hanya untuk kemudahan lokal.
# Jangan pernah dipakai di production.
DEV_SECRET_KEY = "django-insecure-development-only-do-not-use-in-production"

if not SECRET_KEY:
    SECRET_KEY = DEV_SECRET_KEY

DEBUG = True

ALLOWED_HOSTS = sorted(
    {
        "127.0.0.1",
        "localhost",
        "0.0.0.0",
        "testserver",
        *_ENV_ALLOWED_HOSTS,
    }
)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
