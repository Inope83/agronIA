"""Helper untuk membaca konfigurasi dari environment variable.

Tujuan modul ini:
- Semua konfigurasi sensitif (secret key, debug, host) dibaca dari environment.
- File `.env` dibaca tanpa library tambahan, sehingga tidak menambah dependency.
- Nilai yang sudah ada di environment asli selalu menang, sehingga CI/CD atau
  secret manager bisa meng-override file `.env`.
"""

from __future__ import annotations

import os
from pathlib import Path

# Folder `ai-model/`
BASE_DIR = Path(__file__).resolve().parent.parent

_TRUE_VALUES = {"1", "true", "yes", "on"}


def load_dotenv(path: Path | None = None) -> None:
    """Muat pasangan KEY=VALUE dari file `.env` ke `os.environ`.

    Variabel yang sudah ada tidak ditimpa. File yang tidak ada diabaikan
    diam-diam supaya konfigurasi bisa sepenuhnya relying on environment.
    """
    env_file = path if path is not None else BASE_DIR / ".env"
    if not env_file.is_file():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def get_bool(name: str, default: bool = False) -> bool:
    """Baca variabel boolean dari environment."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in _TRUE_VALUES


def get_int(name: str, default: int) -> int:
    """Baca variabel integer dari environment, dengan fallback bila tidak valid."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def get_float(name: str, default: float) -> float:
    """Baca variabel float dari environment, dengan fallback bila tidak valid."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return float(raw.strip())
    except ValueError:
        return default


def get_list(name: str, default: str = "") -> list[str]:
    """Baca variabel daftar dari environment, dipisah dengan koma."""
    raw = os.environ.get(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]
