"""Pengaturan Django yang dipakai bersama oleh semua environment.

Pilih environment dengan mengubah `DJANGO_SETTINGS_MODULE`:
- Development: `config.settings.development` (nilai bawaan di `manage.py`)
- Production:  `config.settings.production`
"""

from __future__ import annotations

import os
from pathlib import Path

from config.env import get_bool, get_float, get_int, get_list, load_dotenv

# Folder `ai-model/`
BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")


# --- Core ----------------------------------------------------------------

# Di production, `config.settings.production` akan menolak nilai kosong.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")

DEBUG = get_bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = get_list("DJANGO_ALLOWED_HOSTS")


# --- Aplikasi ------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "accounts",
    "agriculture",
    "analysis",
    "ai_service",
    "common",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# --- Database ------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# --- Autentikasi ---------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Umur token autentikasi (hari). 0 = tidak kedaluwarsa.
AUTH_TOKEN_TTL_DAYS = get_int("DJANGO_AUTH_TOKEN_TTL_DAYS", 0)


# --- Django REST Framework ----------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "common.exceptions.api_exception_handler",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}


# --- Media & upload ------------------------------------------------------

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Batas ukuran unggahan, dibaca dari environment (megabyte).
MAX_UPLOAD_SIZE_MB = get_int("DJANGO_MAX_UPLOAD_SIZE_MB", 10)
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Batas bawaan Django untuk body permintaan (10 MB).
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE_BYTES
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024


# --- Internationalization ------------------------------------------------

LANGUAGE_CODE = "id"
TIME_ZONE = "Asia/Makassar"
USE_I18N = True
USE_TZ = True


# --- Static files --------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


# --- AI service ----------------------------------------------------------

# Lokasi file bobot model. Kosong selama model belum tersedia.
AI_MODEL_PATH = os.environ.get("AI_MODEL_PATH", "")

# Ambang confidence. Di bawah nilai ini hasil dianggap belum meyakinkan.
AI_CONFIDENCE_THRESHOLD = get_float("AI_CONFIDENCE_THRESHOLD", 0.60)

# Ukuran input model (piksel). Wajib konsisten dengan training.
AI_IMAGE_SIZE = get_int("AI_IMAGE_SIZE", 224)


# --- Logging -------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}


# --- Default -------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
