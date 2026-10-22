"""Serializer untuk permintaan dan hasil analisis."""

from __future__ import annotations

from django.conf import settings
from rest_framework import serializers

from agriculture.models import Crop, Disease
from analysis.models import Analysis, AnalysisFeedback
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
    disease = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()

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
            "disease",
            "feedback",
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

    def get_disease(self, obj: Analysis) -> dict | None:
        """Panduan penyakit untuk hasil yang berhasil.

        Hanya dikirim untuk analisis `completed`; analisis gagal tidak boleh
        terlihat seolah-olah memiliki diagnosis.
        """
        if obj.status != Analysis.Status.COMPLETED or obj.predicted_disease is None:
            return None

        disease = obj.predicted_disease
        return {
            "code": disease.code,
            "name": disease.name,
            "name_local": disease.name_local,
            "symptoms": disease.symptoms,
            "prevention": disease.prevention,
            "management": disease.management,
            "source": disease.source,
        }

    def get_feedback(self, obj: Analysis) -> dict | None:
        """Umpan balik pengguna, bila sudah pernah dikirim."""
        feedback = getattr(obj, "feedback", None)
        if feedback is None:
            return None
        return AnalysisFeedbackSerializer(feedback).data


class AnalysisFeedbackSerializer(serializers.ModelSerializer):
    """Validasi dan bentuk respons umpan balik hasil analisis."""

    suggested_disease = serializers.SlugRelatedField(
        slug_field="code",
        queryset=Disease.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    note = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )

    class Meta:
        model = AnalysisFeedback
        fields = [
            "id",
            "is_correct",
            "suggested_disease",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        """Prediksi yang dianggap benar tidak boleh punya usulan kelas lain."""
        if attrs.get("is_correct") and attrs.get("suggested_disease"):
            raise serializers.ValidationError(
                {
                    "suggested_disease": (
                        "Kosongkan bila prediksi dianggap benar."
                    )
                }
            )
        return attrs
