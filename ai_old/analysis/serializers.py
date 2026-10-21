"""Serializer untuk permintaan dan hasil analisis."""

from __future__ import annotations

from django.conf import settings
from rest_framework import serializers

from agriculture.models import Crop
from analysis.models import Analysis
from analysis.validators import validate_image_file


class AnalysisCreateSerializer(serializers.Serializer):
    """Validasi payload permintaan analisis.

    `crop` opsional pada level API karena dukungan jenis tanaman masih
    bergantung pada model yang dipilih. Bila diberikan, nilainya harus
    menunjuk tanaman yang aktif.
    """

    image = serializers.ImageField(write_only=True)
    crop = serializers.SlugRelatedField(
        slug_field="code",
        queryset=Crop.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )

    def validate_image(self, image):
        """Terapkan aturan validasi berkas di luar `ImageField`."""
        validate_image_file(image)
        return image

    def validate(self, attrs):
        """Cek ukuran maksimum berkas sebelum masuk ke model."""
        request = self.context.get("request")
        max_size = settings.MAX_UPLOAD_SIZE_BYTES
        if request is not None:
            content_length = request.META.get("CONTENT_LENGTH") or "0"
            try:
                if int(content_length) > max_size:
                    raise serializers.ValidationError(
                        {
                            "image": [
                                f"Ukuran permintaan melebihi batas "
                                f"{settings.MAX_UPLOAD_SIZE_MB} MB."
                            ]
                        }
                    )
            except (TypeError, ValueError):
                pass
        return attrs


class AnalysisSerializer(serializers.ModelSerializer):
    """Bentuk respons hasil analisis, mengikuti `docs/api.md`."""

    crop = serializers.SlugRelatedField(slug_field="code", read_only=True)
    predicted_disease = serializers.SlugRelatedField(
        slug_field="code", read_only=True
    )
    image_url = serializers.SerializerMethodField()
    prediction = serializers.SerializerMethodField()

    class Meta:
        model = Analysis
        fields = [
            "id",
            "status",
            "crop",
            "predicted_disease",
            "confidence",
            "model_version",
            "message",
            "image_url",
            "prediction",
            "created_at",
        ]
        read_only_fields = fields

    def get_image_url(self, obj: Analysis) -> str | None:
        """URL gambar privat milik pemilik record.

        Berkas tidak dilayani lewat URL media statis karena URL tersebut
        bisa diakses siapa saja. Yang dipakai adalah endpoint khusus yang
        memeriksa kepemilikan.
        """
        if not obj.image:
            return None
        return f"/api/v1/analyses/{obj.id}/image/"

    def get_prediction(self, obj: Analysis) -> dict | None:
        """Ringkasan prediksi, atau `None` bila analisis tidak berhasil."""
        if obj.status != Analysis.Status.COMPLETED:
            return None
        if obj.predicted_disease is None and obj.confidence is None:
            return None

        return {
            "class_id": obj.predicted_disease.code if obj.predicted_disease else None,
            "label": obj.predicted_disease.name if obj.predicted_disease else None,
            "confidence": obj.confidence,
            "model_version": obj.model_version or None,
            "is_confident": (
                obj.confidence is not None
                and obj.confidence >= settings.AI_CONFIDENCE_THRESHOLD
            ),
        }
