"""Endpoint baca data pertanian."""

from __future__ import annotations

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from agriculture.models import AgriculturalResource, Crop, Disease
from agriculture.serializers import (
    AgriculturalResourceSerializer,
    CropSerializer,
    DiseaseSerializer,
)


class CropViewSet(viewsets.ReadOnlyModelViewSet):
    """Daftar tanaman yang didukung."""

    queryset = Crop.objects.filter(is_active=True)
    serializer_class = CropSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    lookup_field = "code"


class DiseaseViewSet(viewsets.ReadOnlyModelViewSet):
    """Daftar informasi penyakit yang sudah ditinjau."""

    queryset = Disease.objects.filter(is_active=True).prefetch_related("crops")
    serializer_class = DiseaseSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    lookup_field = "code"


class AgriculturalResourceViewSet(viewsets.ReadOnlyModelViewSet):
    """Daftar materi belajar."""

    queryset = AgriculturalResource.objects.all()
    serializer_class = AgriculturalResourceSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"
