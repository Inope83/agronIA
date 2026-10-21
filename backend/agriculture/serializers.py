"""Serializer untuk data pertanian."""

from __future__ import annotations

from rest_framework import serializers

from agriculture.models import AgriculturalResource, Crop, Disease


class CropSerializer(serializers.ModelSerializer):
    """Representasi tanaman yang dikirim ke aplikasi."""

    class Meta:
        model = Crop
        fields = ["id", "code", "name", "name_local", "description"]
        read_only_fields = fields


class DiseaseSerializer(serializers.ModelSerializer):
    """Representasi informasi penyakit beserta panduannya."""

    crop_codes = serializers.SlugRelatedField(
        source="crops",
        many=True,
        read_only=True,
        slug_field="code",
    )

    class Meta:
        model = Disease
        fields = [
            "id",
            "code",
            "name",
            "name_local",
            "crop_codes",
            "symptoms",
            "prevention",
            "management",
            "source",
        ]
        read_only_fields = fields


class AgriculturalResourceSerializer(serializers.ModelSerializer):
    """Representasi materi belajar."""

    class Meta:
        model = AgriculturalResource
        fields = [
            "id",
            "title",
            "summary",
            "body",
            "category",
            "source",
            "is_sample",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
