"""Model data pertanian: tanaman, penyakit, dan sumber belajar."""

from __future__ import annotations

from django.db import models


class Crop(models.Model):
    """Jenis tanaman yang didukung aplikasi.

    `code` dipakai sebagai identifier stabil di API dan sebagai penanda
    kelas pada model AI, sehingga tidak boleh diubah bebas.
    """

    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    name_local = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nama dalam bahasa lokal, misalnya Tetum atau Portugis.",
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Tanaman"
        verbose_name_plural = "Tanaman"

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class Disease(models.Model):
    """Informasi penyakit tanaman beserta panduan penanganan.

    Field `source` wajib diisi. Setiap panduan yang ditampilkan ke pengguna
    harus punya sumber yang diketahui, sesuai `docs/security.md` bagian
    "Privacy and Data Minimization" dan `docs/ui-ux.md` bagian Learn Screen.
    """

    code = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=150)
    name_local = models.CharField(max_length=150, blank=True)
    crops = models.ManyToManyField(
        Crop,
        related_name="diseases",
        blank=True,
        help_text="Tanaman yang dapat terserang penyakit ini.",
    )
    symptoms = models.TextField(
        blank=True,
        help_text="Gejala yang bisa diamati oleh petani.",
    )
    prevention = models.TextField(
        blank=True,
        help_text="Langkah pencegahan.",
    )
    management = models.TextField(
        blank=True,
        help_text="Langkah penanganan setelah penyakit terdeteksi.",
    )
    source = models.TextField(
        help_text="Sumber informasi, misalnya nama lembaga atau tautan rujukan.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Penyakit"
        verbose_name_plural = "Penyakit"

    def __str__(self) -> str:
        return self.name


class AgriculturalResource(models.Model):
    """Materi belajar yang tidak bergantung pada hasil prediksi AI."""

    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=300, blank=True)
    body = models.TextField(blank=True)
    category = models.CharField(max_length=80, blank=True)
    source = models.CharField(
        max_length=300,
        blank=True,
        help_text="Sumber materi. Kosongkan hanya untuk materi samples saat pengembangan.",
    )
    is_sample = models.BooleanField(
        default=False,
        help_text="Tandai True untuk materi contoh yang belum ditinjau ahli.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Sumber Belajar"
        verbose_name_plural = "Sumber Belajar"

    def __str__(self) -> str:
        return self.title
