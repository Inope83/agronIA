"""Model catatan analisis."""

from __future__ import annotations

import uuid

from django.contrib.auth.models import User
from django.db import models

from agriculture.models import Crop, Disease


def analysis_image_path(instance: "Analysis", filename: str) -> str:
    """Tentukan lokasi penyimpanan berkas unggahan.

    Nama berkas dibuat dari UUID supaya nama asli dari perangkat tidak
    dipakai, sehingga tidak ada path traversal dan tidak ada data pribadi
    yang tersimpan di nama berkas.
    """
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    extension = extension if extension.isalnum() else "jpg"
    return f"analyses/{instance.id}.{extension}"


class Analysis(models.Model):
    """Satu permintaan analisis gambar beserta hasilnya."""

    class Status(models.TextChoices):
        PENDING = "pending", "Menunggu"
        PROCESSING = "processing", "Diproses"
        COMPLETED = "completed", "Selesai"
        FAILED = "failed", "Gagal"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="analyses",
    )
    crop = models.ForeignKey(
        Crop,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analyses",
    )
    image = models.ImageField(
        upload_to=analysis_image_path,
        max_length=255,
        help_text="Berkas gambar yang diunggah pengguna.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    predicted_disease = models.ForeignKey(
        Disease,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analyses",
    )
    confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Nilai confidence dari model. Kosong bila model tidak menghasilkannya.",
    )
    model_version = models.CharField(max_length=100, blank=True)
    message = models.TextField(
        blank=True,
        help_text="Penjelasan hasil atau alasan kegagalan, ditulis untuk pengguna umum.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Analisis"
        verbose_name_plural = "Analisis"

    def __str__(self) -> str:
        return f"Analisis {self.id} ({self.status})"


class AnalysisFeedback(models.Model):
    """Koreksi pengguna terhadap hasil analisis.

    Umpan balik dipakai untuk mengevaluasi kualitas model dan menjadi bahan
    validasi berikutnya. Umpan balik tidak mengubah hasil analisis asli.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.OneToOneField(
        Analysis,
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    is_correct = models.BooleanField(
        help_text="Apakah prediksi model sesuai dengan kondisi tanaman.",
    )
    suggested_disease = models.ForeignKey(
        Disease,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="suggested_feedbacks",
        help_text="Kelas yang diusulkan pengguna bila prediksi dianggap salah.",
    )
    note = models.TextField(
        blank=True,
        help_text="Catatan tambahan dari pengguna.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Umpan Balik Analisis"
        verbose_name_plural = "Umpan Balik Analisis"

    def __str__(self) -> str:
        state = "benar" if self.is_correct else "salah"
        return f"Umpan balik {self.analysis_id} ({state})"
