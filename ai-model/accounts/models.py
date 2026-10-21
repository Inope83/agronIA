"""Model profil pengguna."""

from __future__ import annotations

from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Profil tambahan untuk setiap pengguna.

    Data yang dikumpulkan dibatasi seperlunya (lihat `docs/security.md`
    bagian "Privacy and Data Minimization"). Tidak ada nomor telepon atau
    alamat yang dikumpulkan.
    """

    class Role(models.TextChoices):
        FARMER = "farmer", "Petani"
        STUDENT = "student", "Mahasiswa Pertanian"
        EXTENSION = "extension", "Tenaga Pendamping Pertanian"
        ADMIN = "admin", "Administrator"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.FARMER,
    )
    display_name = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profil"

    def __str__(self) -> str:
        return f"Profil {self.user.username} ({self.role})"
